from psr.lakehouse.exceptions import LakehouseError

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

reference_date = "reference_date"

class Client:
    """
    A client for interacting with the PSR Lakehouse database.

    Args:
        server (str): The database server address.
        port (str): The database server port.
        db (str): The name of the database.
        user (str): The username for authentication.
        password (str): The password for authentication.
    """

    def __init__(self, server: str, port: str, db: str, user: str, password: str):
        connection_string = f"postgresql+psycopg://{user}:{password}@{server}:{port}/{db}"
        try:
            self.engine = create_engine(connection_string)
        except ImportError as e:
            raise LakehouseError("SQLAlchemy and psycopg2 are required to use the Lakehouse client.") from e

    def fetch_dataframe_from_sql(self, sql: str, params: dict | None = None) -> pd.DataFrame:
        """
        Fetches a Pandas DataFrame from a SQL query.

        Args:
            sql (str): The SQL query to execute.
            params (dict, optional): A dictionary of parameters to pass to the query. Defaults to None.

        Returns:
            pd.DataFrame: A Pandas DataFrame with the query results.
        """
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql_query(text(sql), connection, params=params)
                if reference_date in df.columns:
                    df[reference_date] = pd.to_datetime(df[reference_date])
                return df
        except SQLAlchemyError as e:
            raise LakehouseError(f"Database error while executing query: {e}") from e

    def fetch_dataframe(
        self,
        table_name: str,
        indices_columns: list[str],
        data_columns: list[str],
        filters: dict | None = None,
        start_reference_date: str | None = None,
        end_reference_date: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetches a Pandas DataFrame from a table.

        Args:
            table_name (str): The name of the table to fetch data from.
            indices_columns (list[str]): A list of indices columns to select.
            data_columns (list[str]): A list of data columns to select.
            filters (dict, optional): A dictionary of filters to apply to the query. Defaults to None.
            start_reference_date (str, optional): The start date for the reference_date filter. Defaults to None.
            end_reference_date (str, optional): The end date for the reference_date filter. Defaults to None.

        Returns:
            pd.DataFrame: A Pandas DataFrame with the query results.
        """

        query = f'SELECT DISTINCT ON ({", ".join(indices_columns)}) {", ".join(indices_columns)}, {", ".join(data_columns)} FROM "{table_name}"'

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
        query += " ORDER BY "
        query += ", ".join([f"{column} ASC" for column in indices_columns])
        query += ", updated_at DESC"

        df = self.fetch_dataframe_from_sql(query, params=params if params else None)

        if reference_date not in indices_columns:
            df = df.drop(columns=[reference_date], errors="ignore")

        df = df.set_index(indices_columns)

        return df

    def list_tables(self, schema: str = "public") -> list[str]:
        """
        Lists all tables in a given schema.

        Args:
            schema (str, optional): The schema to list tables from. Defaults to "public".

        Returns:
            list[str]: A list of table names.
        """
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = :schema AND table_type = 'BASE TABLE'
            AND table_name != 'alembic_version';
            """
        df = self.fetch_dataframe_from_sql(query, params={"schema": schema})
        return df["table_name"].tolist()

    def get_table_info(self, table_name: str, schema: str = "public") -> pd.DataFrame:
        """
        Gets information about a table.

        Args:
            table_name (str): The name of the table.
            schema (str, optional): The schema of the table. Defaults to "public".

        Returns:
            pd.DataFrame: A DataFrame with information about the table's columns.
        """
        query = """
            SELECT column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = :table_name AND table_schema = :schema;
            """
        df = self.fetch_dataframe_from_sql(query, params={"table_name": table_name, "schema": schema})
        return df

    def list_schemas(self) -> list[str]:
        """
        Lists all schemas in the database.

        Returns:
            list[str]: A list of schema names.
        """
        query = """
            SELECT schema_name
            FROM information_schema.schemata;
            """
        df = self.fetch_dataframe_from_sql(query)
        return df["schema_name"].tolist()
