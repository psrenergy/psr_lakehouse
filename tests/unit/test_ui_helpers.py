"""Tests for UI helper functions."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from psr.lakehouse.ui_helpers import (
    UIHelper,
    fetch_data_by_strings,
    format_column_display_name,
    get_data_columns,
    get_datasets_by_organization,
    get_organizations,
    get_streamlit_selector_options,
    get_subsystems,
    parse_date_range_for_filters,
)


class TestUIHelper:
    """Test the UIHelper class."""

    def test_get_organizations(self):
        """Test getting organizations."""
        with patch("psr.lakehouse.ui_helpers.client") as mock_client:
            mock_df = pd.DataFrame(
                {"organization": ["CCEE", "ONS", "CCEE"], "data_name": ["Spot Price", "Stored Energy", "Other Data"]}
            )
            mock_client.list_available_datasets.return_value = mock_df

            helper = UIHelper()
            organizations = helper.get_organizations()

            assert organizations == ["CCEE", "ONS"]
            assert isinstance(organizations, list)

    def test_get_datasets_by_organization(self):
        """Test getting datasets for a specific organization."""
        with patch("psr.lakehouse.ui_helpers.client") as mock_client:
            mock_df = pd.DataFrame(
                {
                    "organization": ["CCEE", "ONS", "CCEE"],
                    "table_name": ["ccee_spot_price", "ons_stored_energy", "ccee_other"],
                    "data_name": ["Spot Price", "Stored Energy", "Other Data"],
                    "description": ["Hourly spot prices", "Energy storage levels", "Other data"],
                }
            )
            mock_client.list_available_datasets.return_value = mock_df

            helper = UIHelper()
            ccee_datasets = helper.get_datasets_by_organization("CCEE")

            assert len(ccee_datasets) == 2
            assert ccee_datasets[0]["data_name"] == "Spot Price"
            assert ccee_datasets[1]["data_name"] == "Other Data"

    def test_get_data_columns(self):
        """Test getting data columns for a dataset."""
        with patch("psr.lakehouse.ui_helpers.client") as mock_client:
            mock_df = pd.DataFrame(
                {
                    "column_name": ["reference_date", "subsystem", "spot_price", "updated_at"],
                    "description": ["Date", "Subsystem", "Price", "Update time"],
                    "unit": [None, None, "R$/MWh", None],
                    "data_type": ["datetime", "string", "float", "datetime"],
                }
            )
            mock_client.get_column_info.return_value = mock_df

            helper = UIHelper()
            columns = helper.get_data_columns("ccee_spot_price")

            # Should only return data columns, not index columns
            assert len(columns) == 1
            assert columns[0]["column_name"] == "spot_price"
            assert columns[0]["unit"] == "R$/MWh"

    def test_get_dataset_info_by_name(self):
        """Test getting dataset info by data name."""
        with patch("psr.lakehouse.ui_helpers.client") as mock_client:
            mock_df = pd.DataFrame(
                {
                    "organization": ["CCEE", "ONS"],
                    "table_name": ["ccee_spot_price", "ons_stored_energy"],
                    "data_name": ["Spot Price", "Stored Energy"],
                    "description": ["Hourly spot prices", "Energy storage levels"],
                }
            )
            mock_client.list_available_datasets.return_value = mock_df

            helper = UIHelper()
            info = helper.get_dataset_info_by_name("Spot Price")

            assert info["table_name"] == "ccee_spot_price"
            assert info["organization"] == "CCEE"

    def test_fetch_data_by_strings(self):
        """Test fetching data using string identifiers."""
        with (
            patch("psr.lakehouse.ui_helpers.client") as mock_client,
            patch("psr.lakehouse.ui_helpers.ccee") as mock_ccee,
        ):
            # Mock the datasets list
            mock_df = pd.DataFrame(
                {
                    "organization": ["CCEE"],
                    "table_name": ["ccee_spot_price"],
                    "data_name": ["Spot Price"],
                    "description": ["Hourly spot prices"],
                }
            )
            mock_client.list_available_datasets.return_value = mock_df

            # Mock the data function
            mock_data = pd.DataFrame({"spot_price": [100.0, 110.0]})
            mock_ccee.spot_price.return_value = mock_data

            helper = UIHelper()
            result = helper.fetch_data_by_strings("CCEE", "Spot Price")

            assert isinstance(result, pd.DataFrame)
            mock_ccee.spot_price.assert_called_once()

    def test_fetch_data_by_strings_with_invalid_dataset(self):
        """Test error handling for invalid dataset."""
        with patch("psr.lakehouse.ui_helpers.client") as mock_client:
            mock_df = pd.DataFrame(
                {
                    "organization": ["CCEE"],
                    "table_name": ["ccee_spot_price"],
                    "data_name": ["Spot Price"],
                    "description": ["Hourly spot prices"],
                }
            )
            mock_client.list_available_datasets.return_value = mock_df

            helper = UIHelper()

            with pytest.raises(ValueError, match="Dataset 'Invalid Data' not found"):
                helper.fetch_data_by_strings("CCEE", "Invalid Data")


class TestConvenienceFunctions:
    """Test the convenience functions."""

    def test_get_organizations_function(self):
        """Test the standalone get_organizations function."""
        with patch("psr.lakehouse.ui_helpers.ui_helper") as mock_helper:
            mock_helper.get_organizations.return_value = ["CCEE", "ONS"]

            result = get_organizations()
            assert result == ["CCEE", "ONS"]

    def test_get_streamlit_selector_options(self):
        """Test getting all selector options at once."""
        with patch("psr.lakehouse.ui_helpers.ui_helper") as mock_helper:
            mock_helper.get_organizations.return_value = ["CCEE", "ONS"]
            mock_helper.get_all_datasets.return_value = [{"table_name": "test"}]
            mock_helper.get_subsystems.return_value = ["N", "S"]

            result = get_streamlit_selector_options()

            assert "organizations" in result
            assert "datasets" in result
            assert "subsystems" in result

    def test_format_column_display_name(self):
        """Test formatting column names for display."""
        # With unit
        column_with_unit = {"column_name": "spot_price", "unit": "R$/MWh", "description": "Price"}
        result = format_column_display_name(column_with_unit)
        assert result == "spot_price (R$/MWh)"

        # Without unit
        column_without_unit = {"column_name": "subsystem", "unit": "", "description": "Subsystem"}
        result = format_column_display_name(column_without_unit)
        assert result == "subsystem"

    def test_parse_date_range_for_filters(self):
        """Test parsing date ranges."""
        from datetime import date

        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)

        result = parse_date_range_for_filters(start_date, end_date)

        assert result["start_reference_date"] == "2024-01-01"
        assert result["end_reference_date"] == "2024-12-31"

        # Test with None values
        result_none = parse_date_range_for_filters(None, None)
        assert result_none == {}
