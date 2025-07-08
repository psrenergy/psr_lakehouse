import os
import boto3
import dotenv
from sqlalchemy import create_engine
from sqlalchemy import text
import pandas as pd

dotenv.load_dotenv()

# Environment variables for the database connection
server = os.getenv("POSTGRES_SERVER")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")

ENDPOINT = server
PORT = port
USER = user
REGION = "us-east-1"
DBNAME = db

client = boto3.client("rds", region_name=REGION)

token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)

connection_string = f"postgresql+psycopg://{USER}:{token}@{ENDPOINT}:{PORT}/{DBNAME}?sslmode=require&sslrootcert=SSLCERTIFICATE"

def main():
    try:
        print("Connecting to the database using SQLAlchemy...")
        
        # Create engine using the connection string
        engine = create_engine(connection_string)

        # Connect to the database
        with engine.connect() as connection:
            print("Connection successful!")
            
            # Execute the query to fetch table names
            sql = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                AND table_name != 'alembic_version';
            """
            # result = conn.execute(query)
            df = pd.read_sql_query(text(sql), connection)
            print(df)
            
            # # Fetch the results and print them
            # query_results = result.fetchall()
            # print(query_results)
    
    except Exception as e:
        print(f"Database connection failed due to {e}")

