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

def load_marginal_cost_weekly_average(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["average"],
        **kwargs,
    )

def load_marginal_cost_weekly_light_load_segment(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["light_load_segment"],
        **kwargs,
    )

def load_marginal_cost_weekly_medium_load_segment(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["medium_load_segment"],
        **kwargs,
    )

def load_marginal_cost_weekly_heavy_load_segment(**kwargs) -> pd.DataFrame:
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["heavy_load_segment"],
        **kwargs,
    )