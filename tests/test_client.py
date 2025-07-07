import psr.lakehouse
import pandas as pd
import dotenv
import tempfile
import os
import pytest
from sqlalchemy.engine.row import Row

dotenv.load_dotenv()
server = os.getenv("POSTGRES_SERVER")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
client = psr.lakehouse.Client(server, port, db, user, password)


def test_ccee_spot_price():
    df = client.fetch_dataframe(
        table_name="ccee_spot_price",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["spot_price"],
        filters={"subsystem": "SOUTHEAST"},
        start_reference_date="2023-05-01 03:00:00",
        end_reference_date="2023-05-01 04:00:00",
    )
    print(df)
