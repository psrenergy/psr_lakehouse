import pytest
import energy_data

def test_ccee_spot_price():
    df = energy_data.ccee_spot_price_dataframe()
    print("DataFrame retrieved successfully.")
    print(df)