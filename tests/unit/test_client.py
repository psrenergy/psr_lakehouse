import pandas as pd
import pytest
import responses

import psr.lakehouse
from psr.lakehouse.exceptions import LakehouseError


def make_query_response(data: list, page: int = 1, page_size: int = 1000, total_count: int | None = None):
    """Helper to create a standard query API response."""
    if total_count is None:
        total_count = len(data)
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0

    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "query_info": {
            "sql": "SELECT ...",
            "columns_selected": len(data[0]) if data else 0,
            "has_filters": True,
            "has_joins": False,
            "has_group_by": False,
        },
    }


class TestFetchDataframe:
    @responses.activate
    def test_fetch_dataframe_basic(self):
        """Test basic data fetching."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "NORTH", "spot_price": 69.04},
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTH", "spot_price": 70.00},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date", "subsystem"],
            data_columns=["spot_price"],
            start_reference_date="2023-05-01",
            end_reference_date="2023-05-02",
        )

        assert len(df) == 2
        assert "spot_price" in df.columns
        assert "subsystem" in df.columns
        # Original implementation only sets reference_date as index
        assert df.index.name == "reference_date"

    @responses.activate
    def test_fetch_dataframe_with_filters(self):
        """Test data fetching with filters."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTHEAST", "spot_price": 69.04},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date", "subsystem"],
            data_columns=["spot_price"],
            filters={"subsystem": "SOUTHEAST"},
        )

        assert len(df) == 1
        # Subsystem is a regular column, not part of the index in original implementation
        assert "subsystem" in df.columns
        assert df["subsystem"].iloc[0] == "SOUTHEAST"

    @responses.activate
    def test_fetch_dataframe_empty_result(self):
        """Test handling of empty results."""
        psr.lakehouse.connector._is_initialized = False

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response([]),
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date", "subsystem"],
            data_columns=["spot_price"],
            start_reference_date="2099-01-01",
            end_reference_date="2099-01-02",
        )

        assert df.empty

    @responses.activate
    def test_fetch_dataframe_pagination(self):
        """Test automatic pagination handling."""
        psr.lakehouse.connector._is_initialized = False

        # First page
        page1_data = [{"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "NORTH", "value": 1}]
        # Second page
        page2_data = [{"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTH", "value": 2}]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json={
                "data": page1_data,
                "pagination": {
                    "page": 1,
                    "page_size": 1,
                    "total_count": 2,
                    "total_pages": 2,
                    "has_next": True,
                    "has_prev": False,
                },
                "query_info": {
                    "sql": "SELECT ...",
                    "columns_selected": 3,
                    "has_filters": False,
                    "has_joins": False,
                    "has_group_by": False,
                },
            },
            status=200,
        )

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json={
                "data": page2_data,
                "pagination": {
                    "page": 2,
                    "page_size": 1,
                    "total_count": 2,
                    "total_pages": 2,
                    "has_next": False,
                    "has_prev": True,
                },
                "query_info": {
                    "sql": "SELECT ...",
                    "columns_selected": 3,
                    "has_filters": False,
                    "has_joins": False,
                    "has_group_by": False,
                },
            },
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ons_energy_load_daily",
            indices_columns=["reference_date", "subsystem"],
            data_columns=["value"],
        )

        assert len(df) == 2
        assert len(responses.calls) == 2

    @responses.activate
    def test_fetch_dataframe_with_aggregation(self):
        """Test data fetching with group_by and aggregation."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"subsystem": "NORTH", "reference_date": "2023-05-01T00:00:00-03:00", "spot_price": 65.0},
            {"subsystem": "SOUTH", "reference_date": "2023-05-01T00:00:00-03:00", "spot_price": 70.0},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date", "subsystem"],
            data_columns=["spot_price"],
            group_by=["subsystem"],
            aggregation_method="avg",
        )

        assert len(df) == 2

    def test_fetch_dataframe_group_by_without_aggregation_raises_error(self):
        """Test that group_by without aggregation_method raises error."""
        with pytest.raises(LakehouseError, match="Both 'group_by' and 'aggregation_method' must be provided together"):
            psr.lakehouse.client.fetch_dataframe(
                table_name="ccee_spot_price",
                indices_columns=["reference_date", "subsystem"],
                data_columns=["spot_price"],
                group_by=["subsystem"],
            )

    def test_fetch_dataframe_aggregation_without_group_by_raises_error(self):
        """Test that aggregation_method without group_by raises error."""
        with pytest.raises(LakehouseError, match="Both 'group_by' and 'aggregation_method' must be provided together"):
            psr.lakehouse.client.fetch_dataframe(
                table_name="ccee_spot_price",
                indices_columns=["reference_date", "subsystem"],
                data_columns=["spot_price"],
                aggregation_method="avg",
            )

    @responses.activate
    def test_high_level_vs_low_level_basic_query(self):
        """Test that fetch_dataframe produces same result as fetch_dataframe_from_query for basic query."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "NORTH", "spot_price": 69.04},
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTH", "spot_price": 70.00},
        ]

        # Setup mock for both calls
        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )
        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # High-level query
        df_high = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date"],
            data_columns=["subsystem", "spot_price"],
            start_reference_date="2023-05-01",
            end_reference_date="2023-05-02",
        )

        # Equivalent low-level query
        df_low = psr.lakehouse.client.fetch_dataframe_from_query(
            {
                "query_data": [
                    "CCEESpotPrice.reference_date",
                    "CCEESpotPrice.subsystem",
                    "CCEESpotPrice.spot_price",
                ],
                "query_filters": [
                    {"column": "CCEESpotPrice.reference_date", "operator": ">=", "value": "2023-05-01"},
                    {"column": "CCEESpotPrice.reference_date", "operator": "<=", "value": "2023-05-02"},
                ],
                "output_timezone": "America/Sao_Paulo",
            }
        )

        # Compare results
        assert len(df_high) == len(df_low)
        assert list(df_high.columns) == list(df_low.columns)
        pd.testing.assert_frame_equal(df_high.sort_index(), df_low.sort_index())

    @responses.activate
    def test_high_level_vs_low_level_with_filters(self):
        """Test that fetch_dataframe with filters produces same result as fetch_dataframe_from_query."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTHEAST", "spot_price": 69.04},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )
        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # High-level query with filters
        df_high = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            indices_columns=["reference_date"],
            data_columns=["subsystem", "spot_price"],
            filters={"subsystem": "SOUTHEAST"},
            start_reference_date="2023-05-01",
            end_reference_date="2023-05-02",
        )

        # Equivalent low-level query
        df_low = psr.lakehouse.client.fetch_dataframe_from_query(
            {
                "query_data": [
                    "CCEESpotPrice.reference_date",
                    "CCEESpotPrice.subsystem",
                    "CCEESpotPrice.spot_price",
                ],
                "query_filters": [
                    {"column": "CCEESpotPrice.subsystem", "operator": "=", "value": "SOUTHEAST"},
                    {"column": "CCEESpotPrice.reference_date", "operator": ">=", "value": "2023-05-01"},
                    {"column": "CCEESpotPrice.reference_date", "operator": "<=", "value": "2023-05-02"},
                ],
                "output_timezone": "America/Sao_Paulo",
            }
        )

        # Compare results
        assert len(df_high) == len(df_low)
        pd.testing.assert_frame_equal(df_high.sort_index(), df_low.sort_index())

    @responses.activate
    def test_high_level_vs_low_level_with_aggregation(self):
        """Test that fetch_dataframe with aggregation produces same result as fetch_dataframe_from_query."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "NORTH", "spot_price": 65.0},
            {"reference_date": "2023-05-01T00:00:00-03:00", "subsystem": "SOUTH", "spot_price": 70.0},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )
        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # High-level query with aggregation
        df_high = psr.lakehouse.client.fetch_dataframe(
            table_name="ccee_spot_price",
            data_columns=["spot_price"],
            group_by=["subsystem"],
            aggregation_method="avg",
            start_reference_date="2023-05-01",
            end_reference_date="2023-05-02",
        )

        # Equivalent low-level query
        df_low = psr.lakehouse.client.fetch_dataframe_from_query(
            {
                "query_data": [
                    "CCEESpotPrice.subsystem",
                    "CCEESpotPrice.spot_price",
                ],
                "query_filters": [
                    {"column": "CCEESpotPrice.reference_date", "operator": ">=", "value": "2023-05-01"},
                    {"column": "CCEESpotPrice.reference_date", "operator": "<=", "value": "2023-05-02"},
                ],
                "group_by": {
                    "group_by_clause": ["CCEESpotPrice.subsystem"],
                    "default_aggregation_method": "avg",
                },
                "output_timezone": "America/Sao_Paulo",
            }
        )

        # Compare results
        assert len(df_high) == len(df_low)
        pd.testing.assert_frame_equal(df_high.sort_index(), df_low.sort_index())

    @responses.activate
    def test_high_level_vs_low_level_with_order_by(self):
        """Test that fetch_dataframe with order_by produces same result as fetch_dataframe_from_query."""
        psr.lakehouse.connector._is_initialized = False

        mock_data = [
            {"reference_date": "2023-05-02T00:00:00-03:00", "plant_type": "WIND", "generation": 45000.0},
            {"reference_date": "2023-05-02T00:00:00-03:00", "plant_type": "HYDRO", "generation": 125000.0},
            {"reference_date": "2023-05-01T00:00:00-03:00", "plant_type": "WIND", "generation": 42000.0},
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )
        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # High-level query with order_by
        df_high = psr.lakehouse.client.fetch_dataframe(
            table_name="ons_power_plant_hourly_generation",
            data_columns=["plant_type", "generation"],
            group_by=["reference_date", "plant_type"],
            aggregation_method="sum",
            datetime_granularity="day",
            order_by=[
                {"column": "reference_date", "direction": "desc"},
                {"column": "plant_type", "direction": "asc"},
            ],
        )

        # Equivalent low-level query
        df_low = psr.lakehouse.client.fetch_dataframe_from_query(
            {
                "query_data": [
                    "ONSPowerPlantHourlyGeneration.reference_date",
                    "ONSPowerPlantHourlyGeneration.plant_type",
                    "ONSPowerPlantHourlyGeneration.generation",
                ],
                "group_by": {
                    "group_by_clause": [
                        "ONSPowerPlantHourlyGeneration.reference_date",
                        "ONSPowerPlantHourlyGeneration.plant_type",
                    ],
                    "default_aggregation_method": "sum",
                    "datetime_granularity": "day",
                },
                "order_by": [
                    {"column": "ONSPowerPlantHourlyGeneration.reference_date", "direction": "desc"},
                    {"column": "ONSPowerPlantHourlyGeneration.plant_type", "direction": "asc"},
                ],
                "output_timezone": "America/Sao_Paulo",
            }
        )

        # Compare results - order matters here
        assert len(df_high) == len(df_low)
        pd.testing.assert_frame_equal(df_high, df_low)

    def test_fetch_dataframe_invalid_aggregation_method_raises_error(self):
        """Test that invalid aggregation method raises error."""
        with pytest.raises(LakehouseError, match="Unsupported aggregation method"):
            psr.lakehouse.client.fetch_dataframe(
                table_name="ccee_spot_price",
                indices_columns=["reference_date", "subsystem"],
                data_columns=["spot_price"],
                group_by=["subsystem"],
                aggregation_method="invalid",
            )

    @responses.activate
    def test_fetch_dataframe_from_query_with_complex_query(self):
        """Test fetch_dataframe_from_query with complex query including joins, group_by, order_by, and filters."""
        psr.lakehouse.connector._is_initialized = False

        # Mock data that would be returned from a join query
        mock_data = [
            {
                "reference_date": "2025-01-05T00:00:00-03:00",
                "subsystem": "SOUTHEAST",
                "energy_load": 45000.5,
                "gross_inflow_energy_mwavg": 12000.3,
            },
            {
                "reference_date": "2025-01-04T00:00:00-03:00",
                "subsystem": "SOUTH",
                "energy_load": 32000.2,
                "gross_inflow_energy_mwavg": 8500.1,
            },
            {
                "reference_date": "2025-01-04T00:00:00-03:00",
                "subsystem": "SOUTHEAST",
                "energy_load": 44500.8,
                "gross_inflow_energy_mwavg": 11800.7,
            },
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # Complex query with all features
        query_body = {
            "query_data": [
                "ONSEnergyLoadDaily.reference_date",
                "ONSEnergyLoadDaily.subsystem",
                "ONSEnergyLoadDaily.energy_load",
                "ONSInflowEnergySubsystem.gross_inflow_energy_mwavg",
            ],
            "query_filters": [
                {
                    "column": "ONSEnergyLoadDaily.reference_date",
                    "operator": ">=",
                    "value": "2025-01-01",
                },
                {
                    "column": "ONSEnergyLoadDaily.reference_date",
                    "operator": "<=",
                    "value": "2025-01-31",
                },
            ],
            "group_by": {
                "group_by_clause": [
                    "ONSEnergyLoadDaily.reference_date",
                    "ONSEnergyLoadDaily.subsystem",
                ],
                "default_aggregation_method": "sum",
                "datetime_granularity": "day",
            },
            "order_by": [
                {
                    "column": "ONSEnergyLoadDaily.reference_date",
                    "direction": "desc",
                },
                {
                    "column": "ONSEnergyLoadDaily.subsystem",
                    "direction": "asc",
                },
            ],
            "joins": [
                {
                    "join_model": "ONSInflowEnergySubsystem",
                    "join_filters": [
                        {
                            "column": "ONSEnergyLoadDaily.reference_date",
                            "value": "ONSInflowEnergySubsystem.reference_date",
                            "operator": "=",
                        },
                        {
                            "column": "ONSEnergyLoadDaily.subsystem",
                            "value": "ONSInflowEnergySubsystem.subsystem",
                            "operator": "=",
                        },
                    ],
                    "is_outer_join": False,
                }
            ],
        }

        df = psr.lakehouse.client.fetch_dataframe_from_query(query_body)

        # Verify results
        assert len(df) == 3
        assert "energy_load" in df.columns
        assert "gross_inflow_energy_mwavg" in df.columns
        assert "subsystem" in df.columns

        # Verify data is ordered correctly (desc by date, asc by subsystem)
        assert df.iloc[0]["subsystem"] == "SOUTHEAST"
        assert df.iloc[1]["subsystem"] == "SOUTH"
        assert df.iloc[2]["subsystem"] == "SOUTHEAST"

        # Verify the API was called with the correct query
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        # The request body should not include the internal _indices_columns
        assert b"_indices_columns" not in request_body

    @responses.activate
    def test_fetch_dataframe_with_all_features(self):
        """Test fetch_dataframe with group_by, datetime_granularity, order_by, and filters."""
        psr.lakehouse.connector._is_initialized = False

        # Mock data aggregated by day
        mock_data = [
            {
                "reference_date": "2025-01-05T00:00:00-03:00",
                "plant_type": "HYDRO",
                "generation": 125000.5,
            },
            {
                "reference_date": "2025-01-05T00:00:00-03:00",
                "plant_type": "WIND",
                "generation": 45000.2,
            },
            {
                "reference_date": "2025-01-04T00:00:00-03:00",
                "plant_type": "HYDRO",
                "generation": 120000.8,
            },
            {
                "reference_date": "2025-01-04T00:00:00-03:00",
                "plant_type": "WIND",
                "generation": 42000.3,
            },
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        df = psr.lakehouse.client.fetch_dataframe(
            table_name="ons_power_plant_hourly_generation",
            data_columns=["plant_type", "generation"],
            start_reference_date="2025-01-01",
            end_reference_date="2025-01-31",
            group_by=["reference_date", "plant_type"],
            aggregation_method="sum",
            datetime_granularity="day",
            order_by=[
                {"column": "reference_date", "direction": "desc"},
                {"column": "plant_type", "direction": "asc"},
            ],
        )

        # Verify results
        assert len(df) == 4
        assert "generation" in df.columns
        assert "plant_type" in df.columns

        # Verify data is ordered correctly (desc by date, asc by plant_type)
        assert df.iloc[0]["plant_type"] == "HYDRO"
        assert df.iloc[1]["plant_type"] == "WIND"
        assert df.iloc[2]["plant_type"] == "HYDRO"
        assert df.iloc[3]["plant_type"] == "WIND"

        # Verify the API was called with correct parameters
        assert len(responses.calls) == 1
        import json

        request_body = json.loads(responses.calls[0].request.body)

        # Check query_data includes both group_by and data columns
        assert "ONSPowerPlantHourlyGeneration.reference_date" in request_body["query_data"]
        assert "ONSPowerPlantHourlyGeneration.plant_type" in request_body["query_data"]
        assert "ONSPowerPlantHourlyGeneration.generation" in request_body["query_data"]

        # Check group_by clause
        assert "group_by" in request_body
        assert request_body["group_by"]["default_aggregation_method"] == "sum"
        assert request_body["group_by"]["datetime_granularity"] == "day"
        assert "ONSPowerPlantHourlyGeneration.reference_date" in request_body["group_by"]["group_by_clause"]
        assert "ONSPowerPlantHourlyGeneration.plant_type" in request_body["group_by"]["group_by_clause"]

        # Check order_by clause
        assert "order_by" in request_body
        assert len(request_body["order_by"]) == 2
        assert request_body["order_by"][0]["column"] == "ONSPowerPlantHourlyGeneration.reference_date"
        assert request_body["order_by"][0]["direction"] == "desc"
        assert request_body["order_by"][1]["column"] == "ONSPowerPlantHourlyGeneration.plant_type"
        assert request_body["order_by"][1]["direction"] == "asc"

        # Check query_filters for date range
        assert "query_filters" in request_body
        date_filters = [f for f in request_body["query_filters"] if "reference_date" in f["column"]]
        assert len(date_filters) == 2
        assert any(f["operator"] == ">=" and f["value"] == "2025-01-01" for f in date_filters)
        assert any(f["operator"] == "<=" and f["value"] == "2025-01-31" for f in date_filters)

    @responses.activate
    def test_fetch_dataframe_from_query_with_joins(self):
        """Test fetch_dataframe_from_query with joins between two tables."""
        psr.lakehouse.connector._is_initialized = False

        # Mock data from joined tables
        mock_data = [
            {
                "reference_date": "2025-01-15T00:00:00-03:00",
                "subsystem": "SOUTHEAST",
                "energy_load": 45000.5,
                "gross_inflow_energy_mwavg": 12000.3,
            },
            {
                "reference_date": "2025-01-10T00:00:00-03:00",
                "subsystem": "SOUTH",
                "energy_load": 32000.2,
                "gross_inflow_energy_mwavg": 8500.1,
            },
            {
                "reference_date": "2025-01-05T00:00:00-03:00",
                "subsystem": "NORTHEAST",
                "energy_load": 28000.8,
                "gross_inflow_energy_mwavg": 7200.5,
            },
        ]

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=make_query_response(mock_data),
            status=200,
        )

        # Query with joins and filters (no group_by or order_by)
        query_body = {
            "query_data": [
                "ONSEnergyLoadDaily.reference_date",
                "ONSEnergyLoadDaily.subsystem",
                "ONSEnergyLoadDaily.energy_load",
                "ONSInflowEnergySubsystem.gross_inflow_energy_mwavg",
                "ONSInflowEnergySubsystem.subsystem",
            ],
            "joins": [
                {
                    "join_model": "ONSInflowEnergySubsystem",
                    "join_filters": [
                        {
                            "column": "ONSEnergyLoadDaily.reference_date",
                            "value": "ONSInflowEnergySubsystem.reference_date",
                            "operator": "=",
                        },
                        {
                            "column": "ONSEnergyLoadDaily.subsystem",
                            "value": "ONSInflowEnergySubsystem.subsystem",
                            "operator": "=",
                        },
                    ],
                    "is_outer_join": False,
                }
            ],
            "query_filters": [
                {
                    "column": "ONSEnergyLoadDaily.reference_date",
                    "operator": ">=",
                    "value": "2025-01-01",
                },
                {
                    "column": "ONSEnergyLoadDaily.reference_date",
                    "operator": "<=",
                    "value": "2025-01-31",
                },
            ],
        }

        df = psr.lakehouse.client.fetch_dataframe_from_query(query_body)

        # Verify results
        assert len(df) == 3
        assert "energy_load" in df.columns
        assert "gross_inflow_energy_mwavg" in df.columns
        assert "subsystem" in df.columns

        # Verify data values
        assert df.iloc[0]["subsystem"] == "SOUTHEAST"
        assert df.iloc[0]["energy_load"] == 45000.5
        assert df.iloc[0]["gross_inflow_energy_mwavg"] == 12000.3

        # Verify the API was called correctly
        assert len(responses.calls) == 1
        import json

        request_body = json.loads(responses.calls[0].request.body)

        # Verify joins are included in the request
        assert "joins" in request_body
        assert len(request_body["joins"]) == 1
        assert request_body["joins"][0]["join_model"] == "ONSInflowEnergySubsystem"
        assert request_body["joins"][0]["is_outer_join"] is False
        assert len(request_body["joins"][0]["join_filters"]) == 2

        # Verify join filters
        join_filters = request_body["joins"][0]["join_filters"]
        assert any(
            f["column"] == "ONSEnergyLoadDaily.reference_date"
            and f["value"] == "ONSInflowEnergySubsystem.reference_date"
            and f["operator"] == "="
            for f in join_filters
        )
        assert any(
            f["column"] == "ONSEnergyLoadDaily.subsystem"
            and f["value"] == "ONSInflowEnergySubsystem.subsystem"
            and f["operator"] == "="
            for f in join_filters
        )

        # Verify query_data includes columns from both tables
        assert "ONSEnergyLoadDaily.energy_load" in request_body["query_data"]
        assert "ONSInflowEnergySubsystem.gross_inflow_energy_mwavg" in request_body["query_data"]

        # Verify query_filters for date range
        assert "query_filters" in request_body
        assert len(request_body["query_filters"]) == 2
        assert any(
            f["column"] == "ONSEnergyLoadDaily.reference_date" and f["operator"] == ">=" and f["value"] == "2025-01-01"
            for f in request_body["query_filters"]
        )
        assert any(
            f["column"] == "ONSEnergyLoadDaily.reference_date" and f["operator"] == "<=" and f["value"] == "2025-01-31"
            for f in request_body["query_filters"]
        )


class TestSchemaEndpoints:
    @responses.activate
    def test_get_schema(self):
        """Test getting schema for a specific table using OpenAPI format."""
        psr.lakehouse.connector._is_initialized = False

        # Mock OpenAPI schema response
        mock_openapi = {
            "components": {
                "schemas": {
                    "CCEESpotPrice": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "nullable": True},
                            "reference_date": {
                                "type": "string",
                                "format": "date-time",
                                "nullable": False,
                                "title": "Reference Date",
                                "description": "Timestamp of the spot price",
                            },
                            "subsystem": {"type": "string", "nullable": True},
                            "spot_price": {
                                "type": "number",
                                "nullable": False,
                                "title": "Spot Price",
                                "description": "Spot price in R$/MWh",
                            },
                            "updated_at": {"type": "string", "format": "date-time"},
                        },
                    }
                }
            }
        }

        responses.add(
            responses.GET,
            "https://test-api.example.com/openapi.json",
            json=mock_openapi,
            status=200,
        )

        schema = psr.lakehouse.client.get_schema("ccee_spot_price")

        assert "reference_date" in schema
        assert "spot_price" in schema
        assert schema["reference_date"]["type"] == "string"
        assert schema["reference_date"]["description"] == "Timestamp of the spot price"
        assert schema["spot_price"]["type"] == "number"

    @responses.activate
    def test_get_model_schema(self):
        """Test getting schema for a specific model (using get_schema)."""
        psr.lakehouse.connector._is_initialized = False

        mock_openapi = {
            "components": {
                "schemas": {
                    "CCEESpotPrice": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "nullable": True},
                            "reference_date": {"type": "string", "format": "date-time"},
                            "spot_price": {"type": "number"},
                            "updated_at": {"type": "string", "format": "date-time"},
                        },
                    }
                }
            }
        }

        responses.add(
            responses.GET,
            "https://test-api.example.com/openapi.json",
            json=mock_openapi,
            status=200,
        )

        # get_model_schema not available, use get_schema instead
        schema = psr.lakehouse.client.get_schema("CCEESpotPrice")

        assert "reference_date" in schema
        assert "spot_price" in schema

    @responses.activate
    def test_list_models(self):
        """Test listing all model names (same as list_tables in current implementation)."""
        psr.lakehouse.connector._is_initialized = False

        mock_openapi = {
            "components": {
                "schemas": {
                    "CCEESpotPrice": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        },
                    },
                    "ONSEnergyLoadDaily": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        },
                    },
                    "ONSStoredEnergySubsystem": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        },
                    },
                    "SomeEnum": {"enum": ["VALUE1", "VALUE2"]},
                }
            }
        }

        responses.add(
            responses.GET,
            "https://test-api.example.com/openapi.json",
            json=mock_openapi,
            status=200,
        )

        # list_models is not available, use list_tables which returns model names
        models = psr.lakehouse.client.list_tables()

        assert "CCEESpotPrice" in models
        assert "ONSEnergyLoadDaily" in models
        assert "ONSStoredEnergySubsystem" in models
        assert "SomeEnum" not in models  # Enums should be filtered out
        assert len(models) == 3

    @responses.activate
    def test_list_tables(self):
        """Test listing all table names (same as list_models)."""
        psr.lakehouse.connector._is_initialized = False

        mock_openapi = {
            "components": {
                "schemas": {
                    "CCEESpotPrice": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        },
                    },
                    "ONSEnergyLoadDaily": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "deleted_at": {"type": "string"},
                        },
                    },
                }
            }
        }

        responses.add(
            responses.GET,
            "https://test-api.example.com/openapi.json",
            json=mock_openapi,
            status=200,
        )

        tables = psr.lakehouse.client.list_tables()

        assert "CCEESpotPrice" in tables
        assert "ONSEnergyLoadDaily" in tables

    @responses.activate
    def test_get_table_columns(self):
        """Test getting column names for a table as a list."""
        psr.lakehouse.connector._is_initialized = False

        mock_openapi = {
            "components": {
                "schemas": {
                    "CCEESpotPrice": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "reference_date": {"type": "string", "format": "date-time", "nullable": False},
                            "spot_price": {"type": "number"},
                            "updated_at": {"type": "string"},
                        },
                    }
                }
            }
        }

        responses.add(
            responses.GET,
            "https://test-api.example.com/openapi.json",
            json=mock_openapi,
            status=200,
        )

        columns = psr.lakehouse.client.get_table_columns("ccee_spot_price")

        assert isinstance(columns, list)
        assert len(columns) == 4
        assert "reference_date" in columns
        assert "spot_price" in columns
        assert "id" in columns
        assert "updated_at" in columns
