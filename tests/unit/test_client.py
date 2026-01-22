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
                                "description": "Timestamp of the spot price"
                            },
                            "subsystem": {"type": "string", "nullable": True},
                            "spot_price": {
                                "type": "number",
                                "nullable": False,
                                "title": "Spot Price",
                                "description": "Spot price in R$/MWh"
                            },
                            "updated_at": {"type": "string", "format": "date-time"},
                        }
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
                        }
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
                        }
                    },
                    "ONSEnergyLoadDaily": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        }
                    },
                    "ONSStoredEnergySubsystem": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "updated_at": {"type": "string"},
                        }
                    },
                    "SomeEnum": {
                        "enum": ["VALUE1", "VALUE2"]
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
                        }
                    },
                    "ONSEnergyLoadDaily": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "deleted_at": {"type": "string"},
                        }
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
                            "reference_date": {
                                "type": "string",
                                "format": "date-time",
                                "nullable": False
                            },
                            "spot_price": {"type": "number"},
                            "updated_at": {"type": "string"},
                        }
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
