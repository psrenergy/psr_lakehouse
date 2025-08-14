import pandas as pd

from ..client import client
from ..metadata import metadata_registry


def stored_energy(**kwargs) -> pd.DataFrame:
    """
    Retrieve reservoir stored energy levels by subsystem from ONS.

    Organization: ONS (Operador Nacional do Sistema Elétrico)
    Data: Stored Energy - Reservoir stored energy levels by subsystem from the Brazilian National System Operator

    Columns:
    - reference_date: Date and time of the observation (datetime)
    - subsystem: Electrical subsystem identifier (string)
    - max_stored_energy: Maximum storage capacity (MWmonth)
    - verified_stored_energy_mwmonth: Verified stored energy amount (MWmonth)
    - verified_stored_energy_percentage: Verified stored energy as percentage of capacity (%)

    Args:
        **kwargs: Additional filtering parameters (filters, start_reference_date, end_reference_date)

    Returns:
        pd.DataFrame: DataFrame with stored energy data indexed by reference_date and subsystem
    """
    return client.fetch_dataframe(
        table_name="ons_stored_energy",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["max_stored_energy", "verified_stored_energy_mwmonth", "verified_stored_energy_percentage"],
        **kwargs,
    )


def load_marginal_cost_weekly(**kwargs) -> pd.DataFrame:
    """
    Retrieve weekly marginal cost of load by subsystem and load segment from ONS.

    Organization: ONS (Operador Nacional do Sistema Elétrico)
    Data: Load Marginal Cost Weekly - Weekly marginal cost of load by subsystem and load segment from the Brazilian National System Operator

    Columns:
    - reference_date: Date and time of the weekly period (datetime)
    - subsystem: Electrical subsystem identifier (string)
    - average: Average marginal cost across all load segments (R$/MWh)
    - light_load_segment: Marginal cost during light load periods (R$/MWh)
    - medium_load_segment: Marginal cost during medium load periods (R$/MWh)
    - heavy_load_segment: Marginal cost during heavy load periods (R$/MWh)

    Args:
        **kwargs: Additional filtering parameters (filters, start_reference_date, end_reference_date)

    Returns:
        pd.DataFrame: DataFrame with marginal cost data indexed by reference_date and subsystem
    """
    return client.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        indices_columns=["reference_date", "subsystem"],
        data_columns=["average", "light_load_segment", "medium_load_segment", "heavy_load_segment"],
        **kwargs,
    )


def get_stored_energy_metadata():
    """Get metadata information for ONS stored energy data."""
    return metadata_registry.get_metadata("ons_stored_energy")


def get_load_marginal_cost_weekly_metadata():
    """Get metadata information for ONS load marginal cost weekly data."""
    return metadata_registry.get_metadata("ons_load_marginal_cost_weekly")
