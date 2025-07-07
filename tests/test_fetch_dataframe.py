import psr.lakehouse

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


def test_ccee_spot_price():
    df = client.fetch_dataframe(
        table_name="ccee_spot_price",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["spot_price"],
        start_reference_date="2023-05-01 03:00:00",
        end_reference_date="2023-05-01 04:00:00",
    )
    print(df)

    expected_index = pd.MultiIndex.from_tuples(
        [
            (pd.to_datetime("2023-05-01 03:00:00"), "NORTH"),
            (pd.to_datetime("2023-05-01 03:00:00"), "NORTHEAST"),
            (pd.to_datetime("2023-05-01 03:00:00"), "SOUTHEAST"),
            (pd.to_datetime("2023-05-01 03:00:00"), "SOUTH"),
        ],
        names=["reference_date", "subsystem"],
    )
    pd.testing.assert_index_equal(df.index, expected_index, check_exact=True)

    expected_series = pd.Series([69.04, 69.04, 69.04, 69.04], index=expected_index, name="spot_price")
    pd.testing.assert_series_equal(df["spot_price"], expected_series)


def test_ons_stored_energy():
    df = client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["max_stored_energy", "verified_stored_energy_mwmonth", "verified_stored_energy_percentage"],
        start_reference_date="2023-05-01",
        end_reference_date="2023-05-02",
    )    
    print(df)
