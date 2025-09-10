import pandas as pd

from ..client import client
from ..metadata import metadata_registry


def stored_energy(**kwargs) -> pd.DataFrame:
    """
    Retrieve reservoir stored energy levels by subsystem from ONS.

    Organization: ONS
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

    Organization: ONS
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


def power_plant_availability(**kwargs) -> pd.DataFrame:
    """
    Retrieve power plant availability data from ONS.

    Organization: ONS
    Data: Power Plant Availability - Power plant availability data from the Brazilian National System Operator

    Columns:
    - reference_date: Date and time of the observation (datetime)
    - subsystem: Electrical subsystem identifier (string)
    - state_code: State code of the generator (string)
    - plant_type: Type of the plant (string)
    - fuel_type: Fuel type of the generator (string, nullable)
    - generator_name: Name of the generator (string)
    - ons_id: ONS ID of the generator (string)
    - ceg: ONS CEG ID of the generator (string, nullable)
    - installed_capacity: Installed capacity of the power plant (MW)
    - operational_availability: Operational availability of the plant (MW)
    - synchronized_availability: Synchronized operational availability (MW)

    Args:
        **kwargs: Additional filtering parameters (filters, start_reference_date, end_reference_date)

    Returns:
        pd.DataFrame: DataFrame with power plant availability data indexed by reference_date, subsystem, ons_id, ceg
    """
    return client.fetch_dataframe(
        table_name="ons_power_plant_availability",
        indices_columns=[
            "reference_date",
            "ons_id",
            "ceg",
            "subsystem",
            "state_code",
            "plant_type",
            "fuel_type",
            "generator_name",
        ],
        data_columns=[
            "installed_capacity",
            "operational_availability",
            "synchronized_availability",
        ],
        **kwargs,
    )


def power_plant_hourly_generation(**kwargs) -> pd.DataFrame:
    """
    Retrieve hourly power generation data from individual power plants in ONS.

    Organization: ONS
    Data: Power Plant Hourly Generation - Hourly power generation data from individual power plants in the Brazilian National System Operator

    Columns:
    - reference_date: Date and time of the generation observation (datetime)
    - subsystem: Electrical subsystem identifier (string)
    - state_code: State code of the generator (string)
    - operation_mode: Operation mode of the generator (string)
    - plant_type: Type of the plant (string)
    - fuel_type: Fuel type of the generator (string, nullable)
    - generator_name: Name of the generator (string)
    - ons_id: ONS ID of the generator (string)
    - ceg: ONS CEG ID of the generator (string, nullable)
    - generation: Forecasted power generation value (MW)

    Args:
        **kwargs: Additional filtering parameters (filters, start_reference_date, end_reference_date)

    Returns:
        pd.DataFrame: DataFrame with hourly generation data indexed by reference_date and ons_id
    """
    return client.fetch_dataframe(
        table_name="ons_power_plant_hourly_generation",
        indices_columns=[
            "reference_date",
            "ons_id",
            "subsystem",
            "state_code",
            "operation_mode",
            "plant_type",
            "fuel_type",
            "generator_name",
            "ceg",
        ],
        data_columns=[
            "generation",
        ],
        **kwargs,
    )


def get_stored_energy_metadata():
    """Get metadata information for ONS stored energy data."""
    return metadata_registry.get_metadata("ons_stored_energy")


def get_load_marginal_cost_weekly_metadata():
    """Get metadata information for ONS load marginal cost weekly data."""
    return metadata_registry.get_metadata("ons_load_marginal_cost_weekly")


def get_power_plant_availability_metadata():
    """Get metadata information for ONS power plant availability data."""
    return metadata_registry.get_metadata("ons_power_plant_availability")


def get_power_plant_hourly_generation_metadata():
    """Get metadata information for ONS power plant hourly generation data."""
    return metadata_registry.get_metadata("ons_power_plant_hourly_generation")
