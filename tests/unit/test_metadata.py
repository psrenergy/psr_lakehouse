from psr.lakehouse.metadata import get_model_name


class TestGetModelName:
    def test_simple_table_name(self):
        """Test table name without underscore returns as-is."""
        assert get_model_name("simple") == "simple"

    def test_ccee_prefix_uppercase(self):
        """Test CCEE prefix is converted to uppercase."""
        assert get_model_name("ccee_spot_price") == "CCEESpotPrice"

    def test_ons_prefix_uppercase(self):
        """Test ONS prefix is converted to uppercase."""
        assert get_model_name("ons_energy_load_daily") == "ONSEnergyLoadDaily"

    def test_ons_stored_energy_subsystem(self):
        """Test ONS stored energy subsystem conversion."""
        assert get_model_name("ons_stored_energy_subsystem") == "ONSStoredEnergySubsystem"

    def test_ons_load_marginal_cost_weekly(self):
        """Test ONS load marginal cost weekly conversion."""
        assert get_model_name("ons_load_marginal_cost_weekly") == "ONSLoadMarginalCostWeekly"

    def test_ons_power_plant_availability(self):
        """Test ONS power plant availability conversion."""
        assert get_model_name("ons_power_plant_availability") == "ONSPowerPlantAvailability"

    def test_ons_power_plant_hourly_generation(self):
        """Test ONS power plant hourly generation conversion."""
        assert get_model_name("ons_power_plant_hourly_generation") == "ONSPowerPlantHourlyGeneration"

    def test_multiple_words(self):
        """Test conversion of multiple words to PascalCase."""
        assert get_model_name("foo_bar_baz") == "FooBarBaz"

    def test_ons_multiple_occurrences(self):
        """Test that ONS is uppercased wherever it appears (it's an acronym)."""
        assert get_model_name("ons_ons_data") == "ONSONSData"

    def test_camel_case_input(self):
        """Test that CamelCase input remains unchanged."""
        assert get_model_name("ONSEnergyLoadDaily") == "ONSEnergyLoadDaily"
