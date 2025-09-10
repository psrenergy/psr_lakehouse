import pandas as pd
from psycopg.errors import InvalidTextRepresentation
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseError, LakehouseInputError
from psr.lakehouse.metadata import metadata_registry

reference_date = "reference_date"


class Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def fetch_dataframe_from_sql(self, sql: str, params: dict | None = None) -> pd.DataFrame:
        try:
            with connector.engine().connect() as connection:
                df = pd.read_sql_query(text(sql), connection, params=params)
                if reference_date in df.columns:
                    df[reference_date] = pd.to_datetime(df[reference_date])
                return df
        except SQLAlchemyError as e:
            if isinstance(e.__cause__, InvalidTextRepresentation):
                raise LakehouseInputError(f"Invalid input error while executing query: {e}") from e
            else:
                raise LakehouseError(f"Database error while executing query: {e}") from e

    def fetch_dataframe(
        self,
        table_name: str,
        indices_columns: list[str],
        data_columns: list[str],
        filters: dict | None = None,
        start_reference_date: str | None = None,
        end_reference_date: str | None = None,
        group_by: list[str] | None = None,
        aggregation_method: str | None = None,
    ) -> pd.DataFrame:
        
        if aggregation_method and aggregation_method not in ["", "sum", "avg", "min", "max"]:
            raise LakehouseError(f"Unsupported aggregation method '{aggregation_method}'. Supported methods are '', 'sum', 'avg', 'min', 'max'.")
        
        if group_by and reference_date not in group_by:
            group_by.append(reference_date)
        
        # Build filter conditions and parameters
        filter_conditions = ['"deleted_at" IS NULL']
        params = {}

        if filters:
            for col, value in filters.items():
                if value is not None:
                    param_name = col.replace(" ", "_")
                    filter_conditions.append(f'"{col}" = :{param_name}')
                    params[param_name] = value

        if start_reference_date:
            filter_conditions.append(f'"{reference_date}" >= :start_reference_date')
            params["start_reference_date"] = start_reference_date

        if end_reference_date:
            filter_conditions.append(f'"{reference_date}" < :end_reference_date')
            params["end_reference_date"] = end_reference_date

        if group_by:
            # Use group_by columns as indices_columns for aggregation queries
            actual_indices = group_by
            # Apply aggregation to data columns if specified
            if aggregation_method and aggregation_method != "":
                select_data_columns = [f"{aggregation_method.upper()}(main.\"{col}\") AS {col}" for col in data_columns]
            else:
                select_data_columns = [f'main."{col}"' for col in data_columns]
            
            # Fully qualified column names for SELECT
            select_indices = [f'main."{col}"' for col in actual_indices]
            
            # Build the main query with table alias
            query = f'SELECT {", ".join(select_indices + select_data_columns)} FROM "{table_name}" main'
            
            # Add JOIN to get latest records per group
            subquery_columns = [f'"{col}"' for col in actual_indices]
            query += f' JOIN (SELECT {", ".join(subquery_columns)}, MAX(updated_at) as latest_updated_at FROM "{table_name}"'
            
            # Apply filters in subquery
            subquery_filter_conditions = []
            for condition in filter_conditions:
                subquery_filter_conditions.append(condition)
            
            if subquery_filter_conditions:
                query += " WHERE " + " AND ".join(subquery_filter_conditions)
            
            query += f' GROUP BY {", ".join(subquery_columns)}) latest_per_group'
            
            # JOIN conditions
            join_conditions = [f'main."{col}" = latest_per_group."{col}"' for col in actual_indices]
            join_conditions.append('main.updated_at = latest_per_group.latest_updated_at')
            query += " ON " + " AND ".join(join_conditions)
            
            # Apply main table filters
            main_filter_conditions = []
            for condition in filter_conditions:
                # Prefix main table conditions with 'main.'
                if condition.startswith('"deleted_at"'):
                    main_filter_conditions.append('main."deleted_at" IS NULL')
                elif condition.startswith('"reference_date"'):
                    main_filter_conditions.append(condition.replace(f'"{reference_date}"', f'main."{reference_date}"'))
                else:
                    # Handle other filter conditions by prefixing with main.
                    for col, value in (filters or {}).items():
                        if f'"{col}"' in condition:
                            main_filter_conditions.append(condition.replace(f'"{col}"', f'main."{col}"'))
                            break
                    else:
                        if 'main.' not in condition:
                            main_filter_conditions.append(condition)
            
            if main_filter_conditions:
                query += " WHERE " + " AND ".join(main_filter_conditions)
            
            # GROUP BY for aggregation
            if aggregation_method and aggregation_method != "":
                group_by_columns = [f'main."{col}"' for col in actual_indices]
                query += " GROUP BY " + ", ".join(group_by_columns)
            
            # ORDER BY
            order_columns = [f'main."{col}" ASC' for col in actual_indices]
            query += " ORDER BY " + ", ".join(order_columns)
            
            # Set indices_columns for final processing
            indices_columns = actual_indices
        else:
            # Non-aggregated query (original logic)
            select_indices = [f'"{col}"' for col in indices_columns]
            select_data_columns = [f'"{col}"' for col in data_columns]
            
            query = f'SELECT DISTINCT ON ({", ".join(select_indices)}) {", ".join(select_indices + select_data_columns)} FROM "{table_name}"'
            query += " WHERE " + " AND ".join(filter_conditions)
            query += " ORDER BY " + ", ".join([f'"{column}" ASC' for column in indices_columns]) + ", updated_at DESC"

        df = self.fetch_dataframe_from_sql(query, params=params if params else None)

        if reference_date not in indices_columns:
            df = df.drop(columns=[reference_date], errors="ignore")

        df = df.set_index(indices_columns)

        return df

    def list_tables(self, schema: str = "public") -> list[str]:
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema AND table_type = 'BASE TABLE'
            AND table_name != 'alembic_version';
            """
        df = self.fetch_dataframe_from_sql(query, params={"schema": schema})
        return df["table_name"].tolist()

    def get_table_info(self, table_name: str, schema: str = "public") -> pd.DataFrame:
        query = """
            SELECT column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = :table_name AND table_schema = :schema;
            """
        df = self.fetch_dataframe_from_sql(query, params={"table_name": table_name, "schema": schema})
        return df

    def list_schemas(self) -> list[str]:
        query = """
            SELECT schema_name
            FROM information_schema.schemata;
            """
        df = self.fetch_dataframe_from_sql(query)
        return df["schema_name"].tolist()

    def get_table_metadata(self, table_name: str):
        """Get metadata for a specific table."""
        return metadata_registry.get_metadata(table_name)

    def list_available_datasets(self) -> pd.DataFrame:
        """List all available datasets with their metadata."""
        datasets = []
        for table_name, metadata in metadata_registry.get_all_metadata().items():
            datasets.append(
                {
                    "table_name": table_name,
                    "organization": metadata.organization,
                    "data_name": metadata.data_name,
                    "description": metadata.description,
                    "columns_count": len(metadata.columns),
                }
            )
        return pd.DataFrame(datasets)

    def get_column_info(self, table_name: str) -> pd.DataFrame:
        """Get detailed column information including units for a specific table."""
        metadata = metadata_registry.get_metadata(table_name)
        if not metadata:
            raise LakehouseError(f"No metadata found for table: {table_name}")

        columns_info = []
        for col in metadata.columns:
            columns_info.append(
                {
                    "column_name": col.name,
                    "description": col.description,
                    "unit": col.unit,
                    "data_type": col.data_type,
                    "column_type": col.column_type,
                }
            )
        return pd.DataFrame(columns_info)


client = Client()
