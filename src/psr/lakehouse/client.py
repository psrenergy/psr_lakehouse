"""
This module provides a client for interacting with the PSR Lakehouse database.
"""

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

reference_date = "reference_date"


class LakehouseError(Exception):
    """Custom exception for Lakehouse client errors."""


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
        connection_string = (
            f"postgresql+psycopg://{user}:{password}@{server}:{port}/{db}"
        )
        try:
            self.engine = create_engine(connection_string)
        except ImportError as e:
            raise LakehouseError(
                "SQLAlchemy and psycopg2 are required to use the Lakehouse client."
            ) from e

    def fetch_dataframe_from_sql(
        self, sql: str, params: dict | None = None
    ) -> pd.DataFrame:
        """
        Fetches a Pandas DataFrame from a SQL query.

        Args:
            sql (str): The SQL query to execute.
            params (dict, optional): A dictionary of parameters to pass to the query.
                Defaults to None.

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
        columns: list[str] | None = None,
        filters: dict | None = None,
        order_by: str | None = None,
        ascending: bool = True,
    ) -> pd.DataFrame:
        """
        Fetches a Pandas DataFrame from a table.

        Args:
            table_name (str): The name of the table to fetch data from.
            columns (list[str], optional): A list of columns to select.
                Defaults to None, which selects all columns.
            filters (dict, optional): A dictionary of filters to apply to the query.
                Defaults to None.
            order_by (str, optional): The column to order the results by.
                Defaults to None.
            ascending (bool, optional): Whether to sort in ascending order.
                Defaults to True.

        Returns:
            pd.DataFrame: A Pandas DataFrame with the query results.
        """
        self._validate_table_name(table_name)

        query = f'SELECT {", ".join(columns) if columns else "*"} FROM "{table_name}"'

        if filters:
            filter_conditions = [
                f'"{col}" = :{col.replace(" ", "_")}' for col in filters.keys()
            ]
            query += " WHERE " + " AND ".join(filter_conditions)

        if order_by:
            query += f' ORDER BY "{order_by}" {"ASC" if ascending else "DESC"}'

        params = {k.replace(" ", "_"): v for k, v in filters.items()} if filters else {}

        df = self.fetch_dataframe_from_sql(query, params=params)

        if columns and reference_date not in columns:
            df = df.drop(columns=[reference_date], errors="ignore")

        return df

    def download_table(self, table_name: str, file_path: str, **kwargs) -> None:
        """
        Downloads a table to a CSV file.

        Args:
            table_name (str): The name of the table to download.
            file_path (str): The path to save the CSV file.
            **kwargs: Additional arguments to pass to the fetch_dataframe method.
        """
        self._validate_table_name(table_name)

        if not file_path.lower().endswith(".csv"):
            raise ValueError("Only CSV file format is supported for download.")

        df = self.fetch_dataframe(table_name=table_name, **kwargs)
        df.to_csv(file_path, index=False)

    def list_tables(self, schema: str = "public") -> list[str]:
        """
        Lists all tables in a given schema.

        Args:
            schema (str, optional): The schema to list tables from.
                Defaults to "public".

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
        df = self.fetch_dataframe_from_sql(
            query, params={"table_name": table_name, "schema": schema}
        )
        return df

    def execute_sql(self, sql: str, params: dict | None = None) -> list[tuple]:
        """
        Executes a raw SQL query and returns a list of tuples.

        Args:
            sql (str): The SQL query to execute.
            params (dict, optional): A dictionary of parameters to pass to the query.
                Defaults to None.

        Returns:
            list[tuple]: A list of tuples with the query results.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(sql), params)
                return result.fetchall()
        except SQLAlchemyError as e:
            raise LakehouseError(f"Database error while executing query: {e}") from e

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

    def _validate_table_name(self, table_name: str) -> None:
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")
        if "." in table_name:
            schema, table = table_name.split(".", 1)
            valid_tables = self.list_tables(schema=schema)
            if table not in valid_tables:
                raise ValueError(f"Invalid table name: {table_name}")
        else:
            valid_tables = self.list_tables()
            if table_name not in valid_tables:
                raise ValueError(f"Invalid table name: {table_name}")
