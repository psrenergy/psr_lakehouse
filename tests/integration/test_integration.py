import pytest

from psr.lakehouse import client
from psr.lakehouse.metadata import get_model_name

pytestmark = pytest.mark.integration

TABLE_NAME = "ccee_spot_price"
MODEL_NAME = get_model_name(TABLE_NAME)


# ── Schema & discovery ──────────────────────────────────────────────


class TestSchemaDiscovery:
    def test_list_tables(self):
        tables = client.list_tables()
        assert isinstance(tables, list)
        assert len(tables) > 0
        assert TABLE_NAME in [t.lower() for t in tables] or MODEL_NAME in tables

    def test_get_table_columns(self):
        columns = client.get_table_columns(TABLE_NAME)
        assert isinstance(columns, list)
        assert len(columns) > 0
        assert all(isinstance(c, str) for c in columns)

    def test_get_schema(self):
        schema = client.get_schema(TABLE_NAME)
        assert isinstance(schema, dict)
        assert len(schema) > 0
        for field_name, field_info in schema.items():
            assert "type" in field_info, f"Field '{field_name}' missing 'type'"
            assert "nullable" in field_info, f"Field '{field_name}' missing 'nullable'"
        subsystem_field = schema.get("subsystem")
        assert subsystem_field is not None, "Field 'subsystem' not found in schema"
        assert subsystem_field["type"] == "enum", "Field 'subsystem' is not of type 'enum'"
        assert "enum_values" in subsystem_field, "Field 'subsystem' missing 'enum_values'"
        assert all(s in subsystem_field["enum_values"] for s in ["NORTE", "NORDESTE", "SUL", "SUDESTE"])


# ── Data fetching ────────────────────────────────────────────────────


class TestDataFetching:
    def test_fetch_dataframe(self):
        df = client.fetch_dataframe(
            TABLE_NAME,
            data_columns=[
                "reference_date",
                "spot_price",
            ],
            start_reference_date="2024-01-01",
            end_reference_date="2024-01-02",
        )
        assert not df.empty
        assert len(df) > 0

    def test_fetch_dataframe_from_query(self):
        json_body = {
            "query_data": [
                f"{MODEL_NAME}.reference_date",
                f"{MODEL_NAME}.spot_price",
            ],
            "query_filters": [
                {
                    "column": f"{MODEL_NAME}.reference_date",
                    "value": "2024-01-01",
                    "operator": ">=",
                },
                {
                    "column": f"{MODEL_NAME}.reference_date",
                    "value": "2024-01-02",
                    "operator": "<=",
                },
            ],
            "output_timezone": "America/Sao_Paulo",
        }
        df = client.fetch_dataframe_from_query(json_body)
        assert not df.empty
        assert len(df) > 0


# ── Filters ──────────────────────────────────────────────────────────


class TestFilters:
    def test_fetch_dataframe_with_filters(self):
        df = client.fetch_dataframe(
            TABLE_NAME,
            data_columns=["spot_price", "subsystem"],
            start_reference_date="2024-01-01",
            end_reference_date="2024-01-02",
            filters={"subsystem": "SUDESTE"},
        )
        assert not df.empty
        assert len(df) > 0


# ── Aggregations ─────────────────────────────────────────────────────


class TestAggregations:
    def test_fetch_dataframe_with_aggregation(self):
        df = client.fetch_dataframe(
            TABLE_NAME,
            data_columns=["spot_price"],
            group_by=["reference_date"],
            aggregation_method="avg",
            datetime_granularity="month",
            start_reference_date="2024-01-01",
            end_reference_date="2024-03-01",
        )
        assert not df.empty
        assert len(df) > 0
