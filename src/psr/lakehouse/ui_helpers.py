"""
UI Helper functions for Streamlit application integration.

This module provides helper functions to support a Streamlit UI with three main selectors:
- Organization (CCEE, ONS)
- Data (dataset names)
- Column (data columns for selected dataset)

It also provides string-based data retrieval functions for easy integration.
"""

from typing import Dict, List, Optional, Tuple

import pandas as pd

from .aliases import ccee, ons
from .client import client
from .metadata import metadata_registry


class UIHelper:
    """Helper class for UI integration with cached data for performance."""

    def __init__(self):
        self._cached_datasets = None
        self._cached_organizations = None
        self._dataset_function_mapping = self._build_function_mapping()

    def _build_function_mapping(self) -> Dict[str, callable]:
        """Build mapping from dataset names to their corresponding functions."""
        return {
            "ccee_spot_price": ccee.spot_price,
            "ons_stored_energy": ons.stored_energy,
            "ons_load_marginal_cost_weekly": ons.load_marginal_cost_weekly,
        }

    def get_organizations(self) -> List[str]:
        """
        Get all available organizations.

        Returns:
            List[str]: List of organization names (e.g., ['CCEE', 'ONS'])
        """
        if self._cached_organizations is None:
            datasets = client.list_available_datasets()
            self._cached_organizations = sorted(datasets["organization"].unique().tolist())
        return self._cached_organizations

    def get_datasets_by_organization(self, organization: str) -> List[Dict[str, str]]:
        """
        Get all datasets for a specific organization.

        Args:
            organization (str): Organization name (e.g., 'CCEE', 'ONS')

        Returns:
            List[Dict[str, str]]: List of dictionaries with 'table_name', 'data_name', and 'description'
        """
        datasets = client.list_available_datasets()
        org_datasets = datasets[datasets["organization"] == organization]

        return [
            {"table_name": row["table_name"], "data_name": row["data_name"], "description": row["description"]}
            for _, row in org_datasets.iterrows()
        ]

    def get_all_datasets(self) -> List[Dict[str, str]]:
        """
        Get all available datasets across all organizations.

        Returns:
            List[Dict[str, str]]: List of dictionaries with dataset information
        """
        datasets = client.list_available_datasets()
        return [
            {
                "table_name": row["table_name"],
                "organization": row["organization"],
                "data_name": row["data_name"],
                "description": row["description"],
            }
            for _, row in datasets.iterrows()
        ]

    def get_data_columns(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get all data columns for a specific dataset.

        Args:
            table_name (str): Table name (e.g., 'ccee_spot_price')

        Returns:
            List[Dict[str, str]]: List of dictionaries with column information
        """
        columns_info = client.get_column_info(table_name)

        # Filter out index columns (reference_date, subsystem, etc.)
        data_columns = []
        for _, row in columns_info.iterrows():
            # Skip typical index columns
            if row["column_name"] not in ["reference_date", "subsystem", "updated_at", "deleted_at"]:
                data_columns.append(
                    {
                        "column_name": row["column_name"],
                        "description": row["description"],
                        "unit": row["unit"] if pd.notna(row["unit"]) else "",
                        "data_type": row["data_type"],
                    }
                )

        return data_columns

    def get_dataset_info_by_name(self, data_name: str) -> Optional[Dict[str, str]]:
        """
        Get dataset information by data name (user-friendly name).

        Args:
            data_name (str): User-friendly data name (e.g., 'Spot Price')

        Returns:
            Optional[Dict[str, str]]: Dataset information or None if not found
        """
        datasets = client.list_available_datasets()
        matching_datasets = datasets[datasets["data_name"] == data_name]

        if matching_datasets.empty:
            return None

        row = matching_datasets.iloc[0]
        return {
            "table_name": row["table_name"],
            "organization": row["organization"],
            "data_name": row["data_name"],
            "description": row["description"],
        }

    def fetch_data_by_strings(
        self, organization: str, data_name: str, columns: Optional[List[str]] = None, **kwargs
    ) -> pd.DataFrame:
        """
        Fetch data using string identifiers (organization and data name).

        Args:
            organization (str): Organization name (e.g., 'CCEE', 'ONS')
            data_name (str): User-friendly data name (e.g., 'Spot Price')
            columns (Optional[List[str]]): Specific columns to retrieve. If None, gets all data columns.
            **kwargs: Additional parameters (filters, start_reference_date, end_reference_date)

        Returns:
            pd.DataFrame: Retrieved data

        Raises:
            ValueError: If organization/data combination is not found
        """
        # Find the dataset
        dataset_info = self.get_dataset_info_by_name(data_name)
        if not dataset_info or dataset_info["organization"] != organization:
            available_datasets = self.get_datasets_by_organization(organization)
            available_names = [d["data_name"] for d in available_datasets]
            raise ValueError(
                f"Dataset '{data_name}' not found for organization '{organization}'. "
                f"Available datasets: {available_names}"
            )

        table_name = dataset_info["table_name"]

        # Get the function for this dataset
        if table_name not in self._dataset_function_mapping:
            raise ValueError(f"No data retrieval function available for table '{table_name}'")

        data_function = self._dataset_function_mapping[table_name]

        # If specific columns are requested, we need to modify the function call
        if columns:
            # Validate requested columns exist
            available_columns = self.get_data_columns(table_name)
            available_column_names = [col["column_name"] for col in available_columns]

            invalid_columns = [col for col in columns if col not in available_column_names]
            if invalid_columns:
                raise ValueError(
                    f"Invalid columns {invalid_columns} for dataset '{data_name}'. "
                    f"Available columns: {available_column_names}"
                )

            # For now, get all data and filter columns afterwards
            # In future, could modify the underlying functions to accept column selection
            df = data_function(**kwargs)
            # Filter to requested columns (keeping the index)
            return df[columns]
        else:
            return data_function(**kwargs)

    def get_subsystems(self, table_name: Optional[str] = None) -> List[str]:
        """
        Get available subsystems.

        Args:
            table_name (Optional[str]): Specific table to get subsystems from. If None, gets from first available table.

        Returns:
            List[str]: List of subsystem identifiers
        """
        if table_name is None:
            # Use the first table that has subsystem data
            table_name = "ccee_spot_price"

        try:
            # Get a small sample to extract subsystem values
            df = client.fetch_dataframe(
                table_name=table_name, indices_columns=["subsystem"], data_columns=["reference_date"], filters=None
            )
            return sorted(df.index.get_level_values("subsystem").unique().tolist())
        except Exception:
            # Fallback to common Brazilian subsystems
            return ["N", "NE", "S", "SE"]


# Create a singleton instance for easy importing
ui_helper = UIHelper()


# Convenience functions for direct import
def get_organizations() -> List[str]:
    """Get all available organizations."""
    return ui_helper.get_organizations()


def get_datasets_by_organization(organization: str) -> List[Dict[str, str]]:
    """Get all datasets for a specific organization."""
    return ui_helper.get_datasets_by_organization(organization)


def get_data_columns(table_name: str) -> List[Dict[str, str]]:
    """Get all data columns for a specific dataset."""
    return ui_helper.get_data_columns(table_name)


def fetch_data_by_strings(
    organization: str, data_name: str, columns: Optional[List[str]] = None, **kwargs
) -> pd.DataFrame:
    """Fetch data using string identifiers."""
    return ui_helper.fetch_data_by_strings(organization, data_name, columns, **kwargs)


def get_subsystems(table_name: Optional[str] = None) -> List[str]:
    """Get available subsystems."""
    return ui_helper.get_subsystems(table_name)


# UI-specific helper functions
def get_streamlit_selector_options() -> Dict[str, List]:
    """
    Get all options needed for Streamlit selectors in a single call.

    Returns:
        Dict[str, List]: Dictionary with 'organizations', 'datasets', and 'subsystems'
    """
    return {
        "organizations": get_organizations(),
        "datasets": ui_helper.get_all_datasets(),
        "subsystems": get_subsystems(),
    }


def format_column_display_name(column_info: Dict[str, str]) -> str:
    """
    Format a column name for display in UI.

    Args:
        column_info (Dict[str, str]): Column information from get_data_columns()

    Returns:
        str: Formatted display name with unit if available
    """
    name = column_info["column_name"]
    unit = column_info.get("unit", "")

    if unit:
        return f"{name} ({unit})"
    return name


def parse_date_range_for_filters(start_date, end_date) -> Dict[str, str]:
    """
    Parse date range inputs for use in data fetching.

    Args:
        start_date: Start date (can be string, datetime, or pandas timestamp)
        end_date: End date (can be string, datetime, or pandas timestamp)

    Returns:
        Dict[str, str]: Dictionary with 'start_reference_date' and 'end_reference_date'
    """
    filters = {}

    if start_date:
        if hasattr(start_date, "strftime"):
            filters["start_reference_date"] = start_date.strftime("%Y-%m-%d")
        else:
            filters["start_reference_date"] = str(start_date)

    if end_date:
        if hasattr(end_date, "strftime"):
            filters["end_reference_date"] = end_date.strftime("%Y-%m-%d")
        else:
            filters["end_reference_date"] = str(end_date)

    return filters
