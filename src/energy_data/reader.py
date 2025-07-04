
import pandas as pd
import psycopg
import sqlalchemy


class PSRDataLakeReader:
    def __init__(self, server: str, port: str, db: str, user: str, password: str):
        self.connection_string = f"dbname='{db}' user='{user}' host='{server}' port='{port}' password='{password}'"

    def fetch_dataframe_from_sql(self, sql: str, params = None) -> pd.DataFrame:
        with psycopg.connect(self.connection_string) as connection:
            return pd.read_sql_query(sql, connection, params=params)

    def fetch_dataframe(self, table_name: str = None, columns: list[str] = None, filters: dict = None, order_by: str = None, ascending: bool = True, rows: int = 100) -> pd.DataFrame:
        self._validate_table_name(table_name)
        
        query = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
        
        if filters: 
            filter_conditions = [f"{col} = %s" for col in filters.keys()]
            query += " WHERE " + " AND ".join(filter_conditions)
        
        if order_by:
            query += f" ORDER BY {order_by} {'ASC' if ascending else 'DESC'}"
        
        query += f" LIMIT {rows}"
        
        params = tuple(filters.values()) if filters else ()
        
        try :
            df = self.fetch_dataframe_from_sql(query, params=params)            
        except sqlalchemy.exc.SQLAlchemyError as e:
            raise ValueError(f"Database error while executing query: {e}")
        except psycopg.Error as e:
            raise ValueError(f"Error while connecting to the database: {e}")
        
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])
        
        if columns and "reference_date" not in columns:
            df = df.drop(columns=["reference_date"], errors='ignore')
        
        return df
    
    
    def sql_query(self, query: str) -> pd.DataFrame:
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")
        
        df = self.fetch_dataframe_from_sql(query)  
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])
        return df

    
    def download_table(self, table_name: str, file_path: str, **kwargs) -> None:
        self._validate_table_name(table_name)
        
        if not file_path.lower().endswith('.csv'):
            raise ValueError("Only CSV file format is supported for download.")

        df = self.fetch_dataframe(table_name=table_name, **kwargs)
        df.to_csv(file_path, index=False)


    def list_tables(self) -> list[str]:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';
        """
        df = self.fetch_dataframe_from_sql(query)
        return df['table_name'].tolist()
        

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        query = f"""
        SELECT column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
        """
        df = self.fetch_dataframe_from_sql(query)
        return df

    def _validate_table_name(self, table_name: str) -> None:
        valid_tables = self.list_tables()
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Table name must be a non-empty string.")
        if table_name not in valid_tables:
            raise ValueError(f"Invalid table name: {table_name}")