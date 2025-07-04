import pytest
import energy_data
import pandas as pd
import tempfile
import os

def test_ccee_spot_price():
    reader = energy_data.PSRDataLakeReader()
    df = reader.fetch_dataframe(
        table_name="ccee_spot_price",
        columns=["reference_date", "spot_price"],
        filters={"reference_date": "2023-10-01"},
        order_by="reference_date",
        ascending=True,
        rows=10
    )
    assert not df.empty
    assert "reference_date" in df.columns
    assert "spot_price" in df.columns
    assert pd.to_datetime(df["reference_date"]).dt.date.eq(pd.to_datetime("2023-10-01").date()).any()

def test_sql_query():
    reader = energy_data.PSRDataLakeReader()
    query = "SELECT * FROM ccee_spot_price WHERE reference_date = '2023-10-01' LIMIT 5"
    df = reader.sql_query(query)
    assert not df.empty
    assert "reference_date" in df.columns
    assert "spot_price" in df.columns
    assert pd.to_datetime(df["reference_date"]).dt.date.eq(pd.to_datetime("2023-10-01").date()).any()


def test_download_table():
    reader = energy_data.PSRDataLakeReader()
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        file_path = tmp.name
    try:
        reader.download_table(
            table_name="ccee_spot_price",
            file_path=file_path,
            columns=["reference_date", "spot_price"],
            filters={"reference_date": "2023-10-01"},
            order_by="reference_date",
            ascending=True,
            rows=10
        )
        df = pd.read_csv(file_path)
        assert not df.empty
        assert "reference_date" in df.columns
        assert "spot_price" in df.columns
        assert pd.to_datetime(df["reference_date"]).dt.date.eq(pd.to_datetime("2023-10-01").date()).any()
    finally:
        os.remove(file_path)

def test_list_tables():
    reader = energy_data.PSRDataLakeReader()
    tables = reader.list_tables()
    assert isinstance(tables, list)
    assert "ccee_spot_price" in tables

def test_get_table_info():
    reader = energy_data.PSRDataLakeReader()
    table_info = reader.get_table_info("ccee_spot_price")
    assert not table_info.empty
    assert "column_name" in table_info.columns
    assert "data_type" in table_info.columns
    assert "is_nullable" in table_info.columns
    assert "character_maximum_length" in table_info.columns 
    assert "reference_date" in table_info["column_name"].values
    assert "spot_price" in table_info["column_name"].values
