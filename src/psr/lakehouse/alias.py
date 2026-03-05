"""Auto-generated table alias methods for the PSR Lakehouse Client.

DO NOT EDIT — regenerate with: make generate-aliases
"""

from __future__ import annotations


def aneel_distributed_generation_projects(self, **kwargs):
    return self.fetch_dataframe(
        table_name="aneel_distributed_generation_projects",
        data_columns=[
            "aneel_upload_date",
            "aneel_upload_period",
            "distributor_cnpj",
            "distributor_code",
            "distributor_name",
            "consumer_class_code",
            "consumer_class_description",
            "tariff_subgroup",
            "state_ibge_code",
            "state_code",
            "region_code",
            "region",
            "municipality_ibge_code",
            "municipality_name",
            "postal_code",
            "consumer_type",
            "owner_cpf_cnpj",
            "owner_name",
            "project_code",
            "project_updated_at",
            "project_modality_description",
            "credit_receiving_units_count",
            "generation_type_code",
            "generation_source_description",
            "project_type",
            "installed_capacity_kw",
            "project_latitude",
            "project_longitude",
            "substation_name",
            "substation_longitude",
            "substation_latitude",
            "modality_type",
            "average_capacity_per_credit_unit_kw",
        ],
        **kwargs,
    )


def ccee_spot_price(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ccee_spot_price", data_columns=["spot_price", "reference_date", "subsystem"], **kwargs
    )


def ccee_spot_price_average_monthly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ccee_spot_price_average_monthly",
        data_columns=["average_spot_price", "reference_date", "subsystem"],
        **kwargs,
    )


def ccee_spot_price_historical_weekly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ccee_spot_price_historical_weekly",
        data_columns=["spot_price", "reference_date", "subsystem", "load_block"],
        **kwargs,
    )


def ceg(self, **kwargs):
    return self.fetch_dataframe(table_name="ceg", data_columns=["value"], **kwargs)


def ceg_data(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ceg_data",
        data_columns=["ceg_id", "state_code", "technology", "fuel_type", "version", "source"],
        **kwargs,
    )


def epe_energy_consumption_monthly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="epe_energy_consumption_monthly",
        data_columns=[
            "reference_date",
            "state_code",
            "region",
            "subsystem",
            "consumer_class",
            "consumer_type",
            "consumption_mwh",
            "consumers",
            "data_version_date",
        ],
        **kwargs,
    )


def generator(self, **kwargs):
    return self.fetch_dataframe(table_name="generator", data_columns=["ons_id"], **kwargs)


def generator_generator_unit(self, **kwargs):
    return self.fetch_dataframe(
        table_name="generator_generator_unit",
        data_columns=["generator_id", "unit_id", "relation_start_date", "relation_end_date"],
        **kwargs,
    )


def generator_unit(self, **kwargs):
    return self.fetch_dataframe(
        table_name="generator_unit", data_columns=["ons_id", "equipment_code", "ceg_id"], **kwargs
    )


def ons_commercial_generation_international_export(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_commercial_generation_international_export",
        data_columns=[
            "reference_date",
            "export_argentina_hydro",
            "export_argentina_total",
            "export_uruguay_hydro",
            "export_uruguay_total",
            "export_thermal",
        ],
        **kwargs,
    )


def ons_controlled_power_flow_program_daily(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_controlled_power_flow_program_daily",
        data_columns=[
            "subsystem",
            "reference_date",
            "level",
            "element_name",
            "element_description",
            "terminal_type",
            "load_value",
        ],
        **kwargs,
    )


def ons_energy_balance_subsystem(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_balance_subsystem",
        data_columns=[
            "subsystem",
            "reference_date",
            "generation_hydraulic",
            "generation_thermal",
            "generation_wind",
            "generation_solar",
            "load",
            "net_interchange",
        ],
        **kwargs,
    )


def ons_energy_import_commercial_block(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_import_commercial_block",
        data_columns=[
            "reference_date",
            "origin_country",
            "agent_name",
            "block_name",
            "programmed_import",
            "dispatched_import",
            "verified_import",
            "price",
        ],
        **kwargs,
    )


def ons_energy_import_price_bids(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_import_price_bids",
        data_columns=["start_date", "end_date", "origin_country", "agent_name", "block_name", "price"],
        **kwargs,
    )


def ons_energy_load_daily(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_load_daily", data_columns=["reference_date", "subsystem", "energy_load"], **kwargs
    )


def ons_energy_load_monthly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_load_monthly", data_columns=["reference_date", "subsystem", "energy_load"], **kwargs
    )


def ons_energy_load_verified(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_energy_load_verified",
        data_columns=[
            "load_area_code",
            "date_of_reference",
            "reference_date",
            "global_load",
            "global_load_net_mmgd",
            "mmgd_load",
            "global_load_consistent",
            "consistency_value",
            "supervised_load",
            "unsupervised_load",
        ],
        **kwargs,
    )


def ons_exchange_international(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_exchange_international",
        data_columns=["destination_country", "reference_date", "exchange"],
        **kwargs,
    )


def ons_exchange_modality(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_exchange_modality",
        data_columns=[
            "converter",
            "reference_date",
            "val_contract",
            "val_emergency",
            "val_opportunity",
            "val_test",
            "val_exceptional",
        ],
        **kwargs,
    )


def ons_exchange_subsystem(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_exchange_subsystem",
        data_columns=["subsystem_from", "subsystem_to", "reference_date", "exchange"],
        **kwargs,
    )


def ons_generator_data(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_generator_data",
        data_columns=[
            "generator_id",
            "ons_set_id",
            "plant_set_id",
            "name",
            "state_code",
            "subsystem",
            "operation_mode",
            "proprietary_agent",
            "operator_agent",
            "plant_type",
            "fuel_type",
        ],
        **kwargs,
    )


def ons_generator_unit_data(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_generator_unit_data",
        data_columns=[
            "name",
            "unit_id",
            "aneel_status",
            "operation_center_code",
            "authorized_capacity",
            "connection_point",
            "generator_unit_name",
            "generator_unit_number",
            "commissioning_date",
            "operation_date",
            "decommissioning_date",
            "nominal_capacity",
            "is_active",
        ],
        **kwargs,
    )


def ons_hydrological_reservoir_data_daily(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_hydrological_reservoir_data_daily",
        data_columns=[
            "reference_date",
            "subsystem",
            "reservoir_type",
            "basin_name",
            "equivalent_reservoir_name",
            "reservoir_id",
            "reservoir_name",
            "reservoir_cascade_order",
            "plant_code",
            "upstream_level",
            "downstream_level",
            "usable_storage_volume_percentage",
            "inflow_rate",
            "flow_rate_turbined",
            "flow_rate_spilled",
            "flow_rate_other_structures",
            "total_outflow_rate",
            "flow_rate_transferred",
            "flow_rate_natural",
            "flow_rate_artificial",
            "flow_rate_incremental",
            "flow_rate_net_evaporation",
            "flow_rate_consumptive_use",
            "flow_rate_gross_incremental",
        ],
        **kwargs,
    )


def ons_hydrological_reservoir_data_hourly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_hydrological_reservoir_data_hourly",
        data_columns=[
            "reference_date",
            "subsystem",
            "reservoir_type",
            "basin_name",
            "reservoir_id",
            "reservoir_name",
            "plant_code",
            "upstream_level",
            "downstream_level",
            "usable_storage_volume_percentage",
            "inflow_rate",
            "flow_rate_turbined",
            "flow_rate_spilled",
            "flow_rate_other_structures",
            "total_outflow_rate",
            "flow_rate_transferred",
            "flow_rate_non_turbinable_spill",
        ],
        **kwargs,
    )


def ons_inflow_energy_basin(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_inflow_energy_basin",
        data_columns=[
            "basin_name",
            "reference_date",
            "gross_inflow_energy_mwavg",
            "gross_inflow_energy_percentage_mlt",
            "storable_inflow_energy_mwavg",
            "storable_inflow_energy_percentage_mlt",
        ],
        **kwargs,
    )


def ons_inflow_energy_equivalent_reservoir(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_inflow_energy_equivalent_reservoir",
        data_columns=[
            "ree_name",
            "reference_date",
            "gross_inflow_energy_mwavg",
            "gross_inflow_energy_percentage_mlt",
            "storable_inflow_energy_mwavg",
            "storable_inflow_energy_percentage_mlt",
        ],
        **kwargs,
    )


def ons_inflow_energy_reservoir(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_inflow_energy_reservoir",
        data_columns=[
            "reservoir_name",
            "planning_code",
            "reservoir_type",
            "basin_name",
            "equivalent_reservoir",
            "subsystem",
            "reference_date",
            "gross_inflow_energy_mwavg",
            "gross_inflow_energy_percentage_mlt",
            "storable_inflow_energy_mwavg",
            "storable_inflow_energy_percentage_mlt",
            "gross_head",
            "mlt_inflow_energy",
        ],
        **kwargs,
    )


def ons_inflow_energy_subsystem(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_inflow_energy_subsystem",
        data_columns=[
            "subsystem",
            "reference_date",
            "gross_inflow_energy_mwavg",
            "gross_inflow_energy_percentage_mlt",
            "storable_inflow_energy_mwavg",
            "storable_inflow_energy_percentage_mlt",
        ],
        **kwargs,
    )


def ons_load_curve(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_load_curve", data_columns=["subsystem", "reference_date", "energy_load"], **kwargs
    )


def ons_load_marginal_cost_semi_hourly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_load_marginal_cost_semi_hourly",
        data_columns=["subsystem", "reference_date", "marginal_cost"],
        **kwargs,
    )


def ons_load_marginal_cost_weekly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_load_marginal_cost_weekly",
        data_columns=[
            "average",
            "light_load_segment",
            "medium_load_segment",
            "heavy_load_segment",
            "reference_date",
            "subsystem",
        ],
        **kwargs,
    )


def ons_power_plant_availability(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_power_plant_availability",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "plant_type",
            "fuel_type",
            "generator_name",
            "ons_id",
            "ceg",
            "installed_capacity",
            "operational_availability",
            "synchronized_availability",
        ],
        **kwargs,
    )


def ons_power_plant_hourly_generation(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_power_plant_hourly_generation",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "operation_mode",
            "plant_type",
            "fuel_type",
            "generator_name",
            "ons_id",
            "ceg",
            "generation",
        ],
        **kwargs,
    )


def ons_solar_curtailment(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_solar_curtailment",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "generator_name",
            "ons_id",
            "ceg",
            "generation",
            "limited_generation",
            "generation_availability",
            "generation_reference",
            "generation_final_reference",
            "reason_code",
            "source_code",
            "description",
            "physical_curtailment",
            "unconstrained_generation",
        ],
        **kwargs,
    )


def ons_solar_curtailment_detailed(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_solar_curtailment_detailed",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "operation_mode",
            "plant_set",
            "generator_name",
            "ons_id",
            "ceg",
            "verified_solar_irradiance",
            "invalid_irradiance_data",
            "estimated_generation",
            "verified_generation",
        ],
        **kwargs,
    )


def ons_spilled_turbinable_energy(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_spilled_turbinable_energy",
        data_columns=[
            "reference_date",
            "subsystem",
            "basin_name",
            "river_name",
            "agent_name",
            "reservoir_name",
            "plant_code",
            "generation",
            "generation_availability",
            "flow_rate_turbined",
            "flow_rate_spilled",
            "flow_rate_non_turbinable_spill",
            "productivity",
            "generation_margin",
            "spilled_energy",
            "spilled_energy_turbinable",
            "flow_rate_turbinable_spill",
        ],
        **kwargs,
    )


def ons_stored_energy_basin(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_stored_energy_basin",
        data_columns=[
            "basin_name",
            "reference_date",
            "max_stored_energy",
            "verified_stored_energy_mwmonth",
            "verified_stored_energy_percentage",
        ],
        **kwargs,
    )


def ons_stored_energy_equivalent_reservoir(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_stored_energy_equivalent_reservoir",
        data_columns=[
            "ree_name",
            "reference_date",
            "max_stored_energy",
            "verified_stored_energy_mwmonth",
            "verified_stored_energy_percentage",
        ],
        **kwargs,
    )


def ons_stored_energy_reservoir(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_stored_energy_reservoir",
        data_columns=[
            "reservoir_name",
            "planning_code",
            "reservoir_type",
            "basin_name",
            "electrical_region",
            "subsystem_id",
            "subsystem_name",
            "downstream_subsystem_id",
            "downstream_subsystem_name",
            "reference_date",
            "ear_reservoir_own_subsystem_mwmonth",
            "ear_reservoir_downstream_subsystem_mwmonth",
            "earmax_reservoir_own_subsystem_mwmonth",
            "earmax_reservoir_downstream_subsystem_mwmonth",
            "ear_reservoir_percentage",
            "ear_total_mwmonth",
            "ear_max_total_mwmonth",
            "contrib_ear_basin",
            "contrib_ear_max_basin",
            "contrib_ear_subsystem",
            "contrib_ear_max_subsystem",
            "contrib_ear_downstream_subsystem",
            "contrib_ear_max_downstream_subsystem",
            "contrib_ear_sin",
            "contrib_ear_max_sin",
        ],
        **kwargs,
    )


def ons_stored_energy_subsystem(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_stored_energy_subsystem",
        data_columns=[
            "max_stored_energy",
            "verified_stored_energy_mwmonth",
            "verified_stored_energy_percentage",
            "reference_date",
            "subsystem",
        ],
        **kwargs,
    )


def ons_thermal_generation_dispatch_reason(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_thermal_generation_dispatch_reason",
        data_columns=[
            "reference_date",
            "load_level",
            "subsystem",
            "generator_name",
            "planning_generator_code",
            "ceg",
            "scheduled_generation_total",
            "scheduled_generation_by_merit",
            "scheduled_generation_by_merit_reference",
            "scheduled_generation_by_merit_no_inflexible",
            "scheduled_generation_inflexible",
            "scheduled_generation_by_merit_inflexible",
            "scheduled_generation_by_merit_pure_inflexible",
            "scheduled_generation_electrical_reason",
            "scheduled_generation_energy_guarantee",
            "scheduled_generation_out_of_merit",
            "scheduled_generation_loss_replacement",
            "scheduled_generation_export",
            "scheduled_generation_power_reserve",
            "scheduled_generation_out_of_merit_substitute",
            "scheduled_generation_unit_commitment",
            "scheduled_generation_curtailed",
            "scheduled_generation_inflexible_dessem",
            "verified_generation_total",
            "verified_generation_by_merit",
            "verified_generation_by_merit_no_inflexible",
            "verified_generation_inflexible",
            "verified_generation_by_merit_inflexible",
            "verified_generation_by_merit_pure_inflexible",
            "verified_generation_electrical_reason",
            "verified_generation_energy_guarantee",
            "verified_generation_out_of_merit",
            "verified_generation_loss_replacement",
            "verified_generation_export",
            "export_code_semi_hourly",
            "verified_generation_power_reserve",
            "reserve_generation_compliance_code",
            "verified_generation_out_of_merit_substitute",
            "verified_generation_unit_commitment",
            "verified_generation_curtailed",
            "electric_restriction",
        ],
        **kwargs,
    )


def ons_thermal_operation_cost(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_thermal_operation_cost",
        data_columns=[
            "reference_week_start",
            "reference_week_end",
            "reference_month",
            "revision_number",
            "subsystem",
            "generator_name",
            "generator_code",
            "cost",
        ],
        **kwargs,
    )


def ons_wind_and_solar_capacity_factor_hourly(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_wind_and_solar_capacity_factor_hourly",
        data_columns=[
            "subsystem",
            "state_code",
            "reference_date",
            "connection_point",
            "connection_point_code",
            "location_name",
            "generator_latitude",
            "generator_longitude",
            "connection_point_latitude",
            "connection_point_longitude",
            "operation_mode",
            "plant_type",
            "plant_set",
            "ons_id",
            "ceg",
            "generation_scheduled",
            "generation_verified",
            "installed_capacity",
            "capacity_factor",
        ],
        **kwargs,
    )


def ons_wind_and_solar_predicted_versus_scheduled(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_wind_and_solar_predicted_versus_scheduled",
        data_columns=[
            "reference_date",
            "level",
            "plant_code",
            "plant_name",
            "generation_predicted",
            "generation_scheduled",
        ],
        **kwargs,
    )


def ons_wind_curtailment(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_wind_curtailment",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "generator_name",
            "ons_id",
            "ceg",
            "generation",
            "limited_generation",
            "generation_availability",
            "generation_reference",
            "generation_final_reference",
            "reason_code",
            "source_code",
            "description",
            "physical_curtailment",
            "unconstrained_generation",
        ],
        **kwargs,
    )


def ons_wind_curtailment_detailed(self, **kwargs):
    return self.fetch_dataframe(
        table_name="ons_wind_curtailment_detailed",
        data_columns=[
            "reference_date",
            "subsystem",
            "state_code",
            "operation_mode",
            "plant_set",
            "generator_name",
            "ons_id",
            "ceg",
            "verified_wind",
            "invalid_wind_data",
            "estimated_generation",
            "verified_generation",
        ],
        **kwargs,
    )


def redemet_meteorological_report(self, **kwargs):
    return self.fetch_dataframe(
        table_name="redemet_meteorological_report",
        data_columns=[
            "station",
            "station_name",
            "reference_date",
            "wind_direction",
            "wind_speed",
            "wind_gust",
            "raw_message",
        ],
        **kwargs,
    )


def register_aliases():
    """Attach all table alias methods to the Client class."""
    from psr.lakehouse.client import Client

    Client.aneel_distributed_generation_projects = aneel_distributed_generation_projects
    Client.ccee_spot_price = ccee_spot_price
    Client.ccee_spot_price_average_monthly = ccee_spot_price_average_monthly
    Client.ccee_spot_price_historical_weekly = ccee_spot_price_historical_weekly
    Client.ceg = ceg
    Client.ceg_data = ceg_data
    Client.epe_energy_consumption_monthly = epe_energy_consumption_monthly
    Client.generator = generator
    Client.generator_generator_unit = generator_generator_unit
    Client.generator_unit = generator_unit
    Client.ons_commercial_generation_international_export = ons_commercial_generation_international_export
    Client.ons_controlled_power_flow_program_daily = ons_controlled_power_flow_program_daily
    Client.ons_energy_balance_subsystem = ons_energy_balance_subsystem
    Client.ons_energy_import_commercial_block = ons_energy_import_commercial_block
    Client.ons_energy_import_price_bids = ons_energy_import_price_bids
    Client.ons_energy_load_daily = ons_energy_load_daily
    Client.ons_energy_load_monthly = ons_energy_load_monthly
    Client.ons_energy_load_verified = ons_energy_load_verified
    Client.ons_exchange_international = ons_exchange_international
    Client.ons_exchange_modality = ons_exchange_modality
    Client.ons_exchange_subsystem = ons_exchange_subsystem
    Client.ons_generator_data = ons_generator_data
    Client.ons_generator_unit_data = ons_generator_unit_data
    Client.ons_hydrological_reservoir_data_daily = ons_hydrological_reservoir_data_daily
    Client.ons_hydrological_reservoir_data_hourly = ons_hydrological_reservoir_data_hourly
    Client.ons_inflow_energy_basin = ons_inflow_energy_basin
    Client.ons_inflow_energy_equivalent_reservoir = ons_inflow_energy_equivalent_reservoir
    Client.ons_inflow_energy_reservoir = ons_inflow_energy_reservoir
    Client.ons_inflow_energy_subsystem = ons_inflow_energy_subsystem
    Client.ons_load_curve = ons_load_curve
    Client.ons_load_marginal_cost_semi_hourly = ons_load_marginal_cost_semi_hourly
    Client.ons_load_marginal_cost_weekly = ons_load_marginal_cost_weekly
    Client.ons_power_plant_availability = ons_power_plant_availability
    Client.ons_power_plant_hourly_generation = ons_power_plant_hourly_generation
    Client.ons_solar_curtailment = ons_solar_curtailment
    Client.ons_solar_curtailment_detailed = ons_solar_curtailment_detailed
    Client.ons_spilled_turbinable_energy = ons_spilled_turbinable_energy
    Client.ons_stored_energy_basin = ons_stored_energy_basin
    Client.ons_stored_energy_equivalent_reservoir = ons_stored_energy_equivalent_reservoir
    Client.ons_stored_energy_reservoir = ons_stored_energy_reservoir
    Client.ons_stored_energy_subsystem = ons_stored_energy_subsystem
    Client.ons_thermal_generation_dispatch_reason = ons_thermal_generation_dispatch_reason
    Client.ons_thermal_operation_cost = ons_thermal_operation_cost
    Client.ons_wind_and_solar_capacity_factor_hourly = ons_wind_and_solar_capacity_factor_hourly
    Client.ons_wind_and_solar_predicted_versus_scheduled = ons_wind_and_solar_predicted_versus_scheduled
    Client.ons_wind_curtailment = ons_wind_curtailment
    Client.ons_wind_curtailment_detailed = ons_wind_curtailment_detailed
    Client.redemet_meteorological_report = redemet_meteorological_report
