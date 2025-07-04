import pytest
from energy_data.retrieve import get_dataframe


def test_get_dataframe():
    df = get_dataframe()
    print("DataFrame retrieved successfully.")
    print(df)