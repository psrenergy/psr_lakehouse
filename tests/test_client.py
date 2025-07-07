import psr.lakehouse

import pytest
import dotenv
import os
import pandas as pd

dotenv.load_dotenv()
server = os.getenv("POSTGRES_SERVER")
port = os.getenv("POSTGRES_PORT")
db = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
client = psr.lakehouse.Client(server, port, db, user, password)


def test_fetch_dataframe_1():
    df = client.fetch_dataframe(
        table_name="ccee_spot_price",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["spot_price"],
        start_reference_date="2023-05-01 03:00:00",
        end_reference_date="2023-05-01 04:00:00",
    )
    print(df)

    # spot_price = [69.04, 69.04, 69.04, 69.04]
    # pd.testing.assert_series_equal(df["spot_price"], pd.Series(spot_price, name="spot_price"))

    # df_dict = df.to_dict(orient='list')
    # print(f"pd.DataFrame({df_dict})")
