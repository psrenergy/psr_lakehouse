import os
import dotenv
import pandas as pd
import psycopg

dotenv.load_dotenv()
server = os.getenv("POSTGRES_SERVER")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
connection_string = f"dbname='{db}' user='{user}' host='{server}' port='{port}' password='{password}'"

def get_dataframe():
    try:
        with psycopg.connect(connection_string) as connection:
            df = pd.read_sql_query("select reference_date, subsystem, spot_price from ccee_spot_price", connection)
            return df

    except (Exception, psycopg.Error) as error:
        print("Error while connecting to Energy Data", error)

