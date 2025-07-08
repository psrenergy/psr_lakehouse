import psycopg2
import boto3
import os
import dotenv

dotenv.load_dotenv()
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

def main():
    try:
        print("Connecting to the database...")
        conn = psycopg2.connect(
            host=ENDPOINT,
            port=PORT,
            database=DBNAME,
            user=USER,
            password=token,
            sslmode='require',
            sslrootcert="SSLCERTIFICATE",
        )
        print("Connection successful!")
        cur = conn.cursor()
        query = """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            AND table_name != 'alembic_version';
            """
        cur.execute(query)
        query_results = cur.fetchall()
        print(query_results)
    except Exception as e:
        print("Database connection failed due to {}".format(e))
