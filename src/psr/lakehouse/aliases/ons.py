import pandas as pd
from ..client import client


def max_stored_energy(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["max_stored_energy"],
        **kwargs,
    )


def verified_stored_energy_mwmonth(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["verified_stored_energy_mwmonth"],
        **kwargs,
    )


def verified_stored_energy_percentage(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["verified_stored_energy_percentage"],
        **kwargs,
    )
