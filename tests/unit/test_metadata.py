import pytest

from psr.lakehouse.metadata import ColumnMetadata, TableMetadata, metadata_registry


class TestMetadataRegistry:
    def test_metadata_registry_singleton(self):
        registry1 = metadata_registry
        from psr.lakehouse.metadata import metadata_registry as registry2

        assert registry1 is registry2

    def test_get_ccee_metadata(self):
        metadata = metadata_registry.get_metadata("ccee_spot_price")
        assert metadata is not None
        assert metadata.organization == "CCEE"
        assert metadata.data_name == "Spot Price"
        assert len(metadata.columns) == 3

    def test_get_ons_stored_energy_metadata(self):
        metadata = metadata_registry.get_metadata("ons_stored_energy")
        assert metadata is not None
        assert metadata.organization == "ONS"
        assert metadata.data_name == "Stored Energy"
        assert len(metadata.columns) == 5

    def test_get_ons_marginal_cost_metadata(self):
        metadata = metadata_registry.get_metadata("ons_load_marginal_cost_weekly")
        assert metadata is not None
        assert metadata.organization == "ONS"
        assert metadata.data_name == "Load Marginal Cost Weekly"
        assert len(metadata.columns) == 6

    def test_get_nonexistent_metadata(self):
        metadata = metadata_registry.get_metadata("nonexistent_table")
        assert metadata is None

    def test_list_tables(self):
        tables = metadata_registry.list_tables()
        expected_tables = ["ccee_spot_price", "ons_stored_energy", "ons_load_marginal_cost_weekly"]
        assert set(tables) == set(expected_tables)

    def test_column_units(self):
        metadata = metadata_registry.get_metadata("ccee_spot_price")
        spot_price_col = metadata.get_column_metadata("spot_price")
        assert spot_price_col.unit == "R$/MWh"

        metadata = metadata_registry.get_metadata("ons_stored_energy")
        energy_col = metadata.get_column_metadata("max_stored_energy")
        assert energy_col.unit == "MWmonth"
