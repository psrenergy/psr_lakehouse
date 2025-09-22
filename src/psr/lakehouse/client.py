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
        time_frequency: str | None = None,
        time_frequency_aggregation_method: str | None = None,
    ) -> pd.DataFrame:
        if bool(group_by) ^ bool(aggregation_method is not None):
            raise LakehouseError("Both 'group_by' and 'aggregation_method' must be provided together.")

        if aggregation_method and aggregation_method not in ["", "sum", "avg", "min", "max"]:
            raise LakehouseError(
                f"Unsupported aggregation method '{aggregation_method}'. Supported methods are '', 'sum', 'avg', 'min', 'max'."
            )

        if time_frequency and time_frequency_aggregation_method:
            if time_frequency_aggregation_method not in ["sum", "avg", "min", "max"]:
                raise LakehouseError(
                    f"Unsupported time frequency aggregation method '{time_frequency_aggregation_method}'. Supported methods are 'sum', 'avg', 'min', 'max'."
                )
            if time_frequency not in ["day", "week", "month", "quarter", "year"]:
                raise LakehouseError(
                    f"Unsupported time frequency '{time_frequency}'. Supported frequencies are 'day', 'week', 'month', 'quarter', 'year'."
                )

        if group_by and reference_date not in group_by:
            group_by.append(reference_date)

        indices_columns = group_by if group_by else indices_columns

        # If we're going to do time frequency aggregation, we need reference_date in the query
        if time_frequency and time_frequency_aggregation_method:
            if reference_date not in indices_columns:
                indices_columns = indices_columns + [reference_date]

        data_columns = (
            [f"{aggregation_method.upper()}({col}) AS {col}" for col in data_columns]
            if aggregation_method
            else data_columns
        )
        query = f"SELECT DISTINCT ON ({', '.join(indices_columns)}) "
        query += f"{', '.join(indices_columns)},"
        query += " MAX(updated_at), " if group_by else ""
        query += f'{", ".join(data_columns)} FROM "{table_name}"'

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

        query += " WHERE " + " AND ".join(filter_conditions)
        if group_by:
            query += " GROUP BY " + ", ".join(group_by)
        query += " ORDER BY "
        query += ", ".join([f"{column} ASC" for column in indices_columns])

        if not group_by:
            query += ", updated_at DESC"

        if time_frequency and time_frequency_aggregation_method:
            # Extract just the column names without the aggregation for the inner query
            inner_data_columns = []
            for col in data_columns:
                if " AS " in col:
                    # Extract the alias (column name after AS)
                    alias = col.split(" AS ")[-1]
                    inner_data_columns.append(alias)
                else:
                    inner_data_columns.append(col)

            # For time frequency aggregation, we want to group by the ORIGINAL indices_columns
            # (before any reference_date was added) and the new reference_date_period
            # Get the original indices_columns without reference_date
            if group_by:
                # If group_by was used, get the original group_by columns minus reference_date
                time_group_columns = [col for col in group_by if col != reference_date]
            else:
                # If no group_by, use the original indices_columns passed to the function
                # We need to reconstruct what the original indices_columns were
                original_indices_columns = [col for col in indices_columns if col != reference_date]
                time_group_columns = original_indices_columns

            query = f"""
                SELECT {", ".join(time_group_columns)}, 
                DATE_TRUNC('{time_frequency}', {reference_date})::date AS reference_date_period,
                {", ".join([f"{time_frequency_aggregation_method.upper()}({col}) AS {col}" for col in inner_data_columns])}
                FROM ({query}
                ) GROUP BY {", ".join(time_group_columns)}, reference_date_period
                ORDER BY {", ".join(time_group_columns)}, reference_date_period ASC
                """

        print("Executing SQL Query:")
        print(query)
        print("With parameters:")
        print(params)

        df = self.fetch_dataframe_from_sql(query, params=params if params else None)

        if reference_date not in indices_columns:
            df = df.drop(columns=[reference_date], errors="ignore")

        # Adjust the index columns if time_frequency was applied
        final_indices_columns = indices_columns.copy()
        if time_frequency and time_frequency_aggregation_method:
            # For time frequency, use only the non-reference_date columns plus reference_date_period
            final_indices_columns = [col for col in indices_columns if col != reference_date]
            final_indices_columns.append("reference_date_period")

        df = df.set_index(final_indices_columns)

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
                    "possible_values": col.values,
                }
            )
        return pd.DataFrame(columns_info)


client = Client()
