import pandas as pd
from psycopg.errors import InvalidTextRepresentation
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseError, LakehouseGroupByFunctionError, LakehouseInputError
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
        group_by: dict[str, str] | None = None,
    ) -> pd.DataFrame:
        if group_by:
            # remove the indices_columns and data_columns if they are not in group_by keys (except reference_date)
            group_by_keys = list(group_by.keys())
            indices_columns = [col for col in indices_columns if col == reference_date or col in group_by_keys]
            data_columns = [col for col in data_columns if col == reference_date or col in group_by_keys]

        query = f'SELECT DISTINCT ON ({", ".join(indices_columns)}) {", ".join(indices_columns)}, {", ".join(data_columns)} FROM "{table_name}"'

        filter_conditions = ['"deleted_at" IS NULL']
        params = {}
        grouping_columns = []

        if group_by:
            # Split columns into grouping columns and aggregation columns
            aggregation_replacements = {}

            if reference_date not in group_by:
                group_by[reference_date] = ""

            for col, func in group_by.items():
                if col not in data_columns + indices_columns:
                    raise LakehouseGroupByFunctionError(
                        f"Column '{col}' in group_by is not in data_columns or indices_columns."
                    )

                # If no function specified or empty string, treat as grouping column
                if not func or func == "":
                    grouping_columns.append(col)
                else:
                    # Validate aggregation function
                    if func.lower() not in ["sum", "avg", "min", "max"]:
                        raise LakehouseGroupByFunctionError(
                            f"Unsupported grouping function '{func}' for column '{col}'."
                        )

                    # Only apply aggregation to data columns (not indices/grouping columns)
                    if col in data_columns:
                        aggregation_replacements[col] = f"{func.upper()}({col}) AS {col}"
                    else:
                        # If it's an index column with an aggregation function, treat it as grouping instead
                        grouping_columns.append(col)

            # Apply aggregation replacements to the query
            for col, replacement in aggregation_replacements.items():
                query = query.replace(col, replacement)

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

        query += " WHERE " + " AND ".join(filter_conditions)
        if group_by:
            query += " GROUP BY " + ", ".join(grouping_columns)
        query += " ORDER BY "
        query += ", ".join([f"{column} ASC" for column in indices_columns])
        query += ", updated_at DESC"

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
