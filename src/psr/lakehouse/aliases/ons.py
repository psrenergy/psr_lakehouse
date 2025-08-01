import pandas as pd

from ..client import client


def stored_energy(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["max_stored_energy", "verified_stored_energy_mwmonth", "verified_stored_energy_percentage"],
        **kwargs,
    )


def load_marginal_cost_weekly(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["average", "light_load_segment", "medium_load_segment", "heavy_load_segment"],
        **kwargs,
    )

