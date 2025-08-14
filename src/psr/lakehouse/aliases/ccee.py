import pandas as pd

from ..client import client
from ..metadata import metadata_registry


def spot_price(**kwargs) -> pd.DataFrame:
    """
    Retrieve hourly electricity spot prices by subsystem from CCEE.

    Organization: CCEE
    Data: Spot Price - Hourly electricity spot prices by subsystem in the Brazilian electricity market

    Columns:
    - reference_date: Date and time of the price observation (datetime)
    - subsystem: Electrical subsystem identifier (string)
    - spot_price: Electricity spot price (R$/MWh)

    Args:
        **kwargs: Additional filtering parameters (filters, start_reference_date, end_reference_date)

    Returns:
        pd.DataFrame: DataFrame with spot price data indexed by reference_date and subsystem
    """
    return client.fetch_dataframe(
        table_name="ccee_spot_price",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["spot_price"],
        **kwargs,
    )


def get_metadata() -> dict:
    """Get metadata information for CCEE spot price data."""
    return metadata_registry.get_metadata("ccee_spot_price")
