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
        columns=["reference_date", "subsystem", "spot_price"],
        filters={"reference_date": "2023-10-01"},
        order_by="reference_date",
        ascending=True,
    )
    print(df)
    assert not df.empty
    assert "reference_date" in df.columns
    assert "spot_price" in df.columns
    assert (
        pd.to_datetime(df["reference_date"])
        .dt.date.eq(pd.to_datetime("2023-10-01").date())
        .any()
    )


def test_ons_stored_energy():
    df = client.fetch_dataframe(
        table_name="ons_stored_energy",
        columns=[
            "reference_date",
            "subsystem",
            "max_stored_energy",
            "verified_stored_energy_mwmonth",
            "verified_stored_energy_percentage",
        ],
        order_by="reference_date",
        ascending=True,
    )
    print(df)
    assert not df.empty
    assert "reference_date" in df.columns
    assert "subsystem" in df.columns
    assert "max_stored_energy" in df.columns
    assert "verified_stored_energy_mwmonth" in df.columns
    assert "verified_stored_energy_percentage" in df.columns


def test_fetch_dataframe_from_sql():
    query = "SELECT * FROM ccee_spot_price WHERE reference_date = :ref_date LIMIT 5"
    df = client.fetch_dataframe_from_sql(query, params={"ref_date": "2023-10-01"})
    assert not df.empty
    assert "reference_date" in df.columns
    assert "spot_price" in df.columns
    assert (
        pd.to_datetime(df["reference_date"])
        .dt.date.eq(pd.to_datetime("2023-10-01").date())
        .any()
    )


def test_download_table():
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        file_path = tmp.name
    try:
        client.download_table(
            table_name="ccee_spot_price",
            file_path=file_path,
            columns=["reference_date", "spot_price"],
            filters={"reference_date": "2023-10-01"},
            order_by="reference_date",
            ascending=True,
        )
        df = pd.read_csv(file_path)
        assert not df.empty
        assert "reference_date" in df.columns
        assert "spot_price" in df.columns
        assert (
            pd.to_datetime(df["reference_date"])
            .dt.date.eq(pd.to_datetime("2023-10-01").date())
            .any()
        )
    finally:
        os.remove(file_path)


def test_list_tables():
    tables = client.list_tables()
    assert isinstance(tables, list)
    assert "ccee_spot_price" in tables


def test_get_table_info():
    table_info = client.get_table_info("ccee_spot_price")
    assert not table_info.empty
    assert "column_name" in table_info.columns
    assert "data_type" in table_info.columns
    assert "is_nullable" in table_info.columns
    assert "character_maximum_length" in table_info.columns
    assert "reference_date" in table_info["column_name"].values
    assert "spot_price" in table_info["column_name"].values


def test_execute_sql():
    query = "SELECT * FROM ccee_spot_price WHERE reference_date = :ref_date"
    results = client.execute_sql(query, params={"ref_date": "2023-10-01"})
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], Row)


def test_list_schemas():
    schemas = client.list_schemas()
    assert isinstance(schemas, list)
    assert "public" in schemas


def test_invalid_table():
    with pytest.raises(ValueError, match="Invalid table name: invalid_table"):
        client.fetch_dataframe(table_name="invalid_table")


def test_invalid_schema():
    with pytest.raises(ValueError, match="Invalid table name: invalid_schema.ccee_spot_price"):
        client.fetch_dataframe(table_name="invalid_schema.ccee_spot_price")


def test_invalid_file_format():
    with pytest.raises(ValueError, match="Only CSV file format is supported for download."):
        client.download_table(table_name="ccee_spot_price", file_path="test.txt")


def test_ccee_spot_price_with_date_range():
    df = client.fetch_dataframe(
        table_name="ccee_spot_price",
        columns=["reference_date", "subsystem", "spot_price"],
        start_reference_date="2023-10-01",
        end_reference_date="2023-10-02",
        order_by="reference_date",
        ascending=True,
    )
    print(df)
    assert not df.empty
    assert "reference_date" in df.columns
    assert "spot_price" in df.columns
    assert (
        pd.to_datetime(df["reference_date"])
        .dt.date.eq(pd.to_datetime("2023-10-01").date())
        .any()
    )
    assert (
        pd.to_datetime(df["reference_date"])
        .dt.date.eq(pd.to_datetime("2023-10-02").date())
        .any()
    )

