import pandas as pd
import psycopg

def get_dataframe(db_connection_string: str, sql_query: str):
    try:
        # Establish a connection to the database using psycopg3
        # The 'with' statement ensures the connection is automatically closed.
        with psycopg.connect(db_connection_string) as conn:
            # Execute the query and fetch the data into a pandas DataFrame
            df = pd.read_sql_query(sql_query, conn)
            return df

    except (Exception, psycopg.Error) as error:
        print("Error while connecting to PostgreSQL", error)

