
import os
import pandas as pd
import dotenv
from sqlalchemy import create_engine

class PSRDataLakeReader:
    def __init__(self):
        dotenv.load_dotenv()
        server = os.getenv("POSTGRES_SERVER")
        port = os.getenv("POSTGRES_PORT")
        db = os.getenv("POSTGRES_DB")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        
        self.engine = create_engine(
            f"postgresql+psycopg2://{user}:{password}@{server}:{port}/{db}"
        )
    
    def retrieve_dataframe(self, table_name: str = None, columns: list[str] = None, filters: dict = None, order_by: str = None, ascending: bool = True, rows: int = 100) -> pd.DataFrame:
        if not table_name:
            raise ValueError("Table name must be provided.")
        
        query = f"SELECT {', '.join(columns) if columns else '*'} FROM {table_name}"
        
        if filters: 
            filter_conditions = [f"{col} = %s" for col in filters.keys()]
            query += " WHERE " + " AND ".join(filter_conditions)
        
        if order_by:
            query += f" ORDER BY {order_by} {'ASC' if ascending else 'DESC'}"
        
        query += f" LIMIT {rows}"
        
        params = tuple(filters.values()) if filters else ()
        
        try :
            df = pd.read_sql(query, con=self.engine, params=params)
        except Exception as e:
            raise ValueError(f"Error executing query: {e}")
        
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])
        
        if columns and "reference_date" not in columns:
            df = df.drop(columns=["reference_date"], errors='ignore')
        
        return df
    
    
    def sql_query(self, query: str) -> pd.DataFrame:
        if not query.strip().lower().startswith("select"):
            raise ValueError("Only SELECT queries are allowed.")
        
        df = pd.read_sql(query, con=self.engine)
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])
        return df

    
    def download_table(self, table_name: str, file_path: str, **kwargs) -> None:
        if not file_path.lower().endswith('.csv'):
            raise ValueError("Only CSV file format is supported for download.")

        df = self.retrieve_dataframe(table_name=table_name, **kwargs)
        df.to_csv(file_path, index=False)


    def list_tables(self) -> list[str]:
        query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE' AND table_name != 'alembic_version';
        """
        df = pd.read_sql(query, con=self.engine)
        return df['table_name'].tolist()
        

    def get_table_info(self, table_name: str) -> pd.DataFrame:
        query = f"""
        SELECT column_name, data_type, is_nullable, character_maximum_length
        FROM information_schema.columns
        WHERE table_name = '{table_name}';
        """
        df = pd.read_sql(query, con=self.engine)
        return df
