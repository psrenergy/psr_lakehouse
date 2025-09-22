from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

SUBSYSTEMS = ["NORTH", "NORTHEAST", "SOUTHEAST", "SOUTH"]
STATE_CODES = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA",
    "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN",
    "RS", "RO", "RR", "SC", "SP", "SE", "TO"
]
PLANT_TYPES = [
    "HYDROELECTRIC", "THERMAL", "NUCLEAR", "WIND", "SOLAR", "PUMPED_STORAGE"
]
OPERATION_MODES = [
    "TYPE_I", "TYPE_II_A" "TYPE_II_B", "TYPE_II_C", "TYPE_III", "TYPE_MMGD"
]

class ColumnType(Enum):
    DATETIME = "datetime"
    CATEGORY = "category"
    IDENTIFIER = "identifier"
    DATA = "data" 
    METADATA = "metadata"


@dataclass
class ColumnMetadata:
    name: str
    description: str
    unit: Optional[str] = None
    data_type: Optional[str] = None
    column_type: Optional[ColumnType] = None
    values: Optional[List[str]] = None


@dataclass
class TableMetadata:
    table_name: str
    organization: str
    data_name: str
    description: str
    columns: List[ColumnMetadata]

    def get_column_metadata(self, column_name: str) -> Optional[ColumnMetadata]:
        return next((col for col in self.columns if col.name == column_name), None)


class MetadataRegistry:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._registry = {}
            cls._instance._initialize_metadata()
        return cls._instance

    def _initialize_metadata(self):
        # CCEE Tables
        self._registry["ccee_spot_price"] = TableMetadata(
            table_name="ccee_spot_price",
            organization="CCEE",
            data_name="Spot Price",
            description="Hourly electricity spot prices by subsystem in the Brazilian electricity market",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the price observation", None, "datetime", ColumnType.DATETIME),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string", ColumnType.IDENTIFIER, values=SUBSYSTEMS),
                ColumnMetadata("spot_price", "Electricity spot price", "R$/MWh", "float", ColumnType.DATA),
            ],
        )

        # ONS Tables
        self._registry["ons_stored_energy"] = TableMetadata(
            table_name="ons_stored_energy",
            organization="ONS",
            data_name="Stored Energy",
            description="Reservoir stored energy levels by subsystem from the Brazilian National System Operator",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the observation", None, "datetime", ColumnType.DATETIME),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string", ColumnType.IDENTIFIER, values=SUBSYSTEMS),
                ColumnMetadata("max_stored_energy", "Maximum storage capacity", "MWmonth", "float", ColumnType.DATA),
                ColumnMetadata("verified_stored_energy_mwmonth", "Verified stored energy amount", "MWmonth", "float", ColumnType.DATA),
                ColumnMetadata(
                    "verified_stored_energy_percentage",
                    "Verified stored energy as percentage of capacity",
                    "%",
                    "float",
                    ColumnType.DATA
                ),
            ],
        )

        self._registry["ons_load_marginal_cost_weekly"] = TableMetadata(
            table_name="ons_load_marginal_cost_weekly",
            organization="ONS",
            data_name="Load Marginal Cost Weekly",
            description="Weekly marginal cost of load by subsystem and load segment from the Brazilian National System Operator",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the weekly period", None, "datetime", ColumnType.DATETIME),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string", ColumnType.IDENTIFIER, values=SUBSYSTEMS),
                ColumnMetadata("average", "Average marginal cost across all load segments", "R$/MWh", "float", ColumnType.DATA),
                ColumnMetadata("light_load_segment", "Marginal cost during light load periods", "R$/MWh", "float", ColumnType.DATA),
                ColumnMetadata("medium_load_segment", "Marginal cost during medium load periods", "R$/MWh", "float", ColumnType.DATA),
                ColumnMetadata("heavy_load_segment", "Marginal cost during heavy load periods", "R$/MWh", "float", ColumnType.DATA),
            ],
        )

        self._registry["ons_power_plant_availability"] = TableMetadata(
            table_name="ons_power_plant_availability",
            organization="ONS",
            data_name="Power Plant Availability",
            description="Power plant availability data from the Brazilian National System Operator",
            columns=[
            ColumnMetadata("reference_date", "Date and time of the observation", None, "datetime", ColumnType.DATETIME),
            ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string", ColumnType.CATEGORY, values=SUBSYSTEMS),
            ColumnMetadata("state_code", "State code of the generator", None, "string", ColumnType.CATEGORY, values=STATE_CODES),
            ColumnMetadata("plant_type", "Type of the plant", None, "string", ColumnType.CATEGORY, values=PLANT_TYPES),
            ColumnMetadata("fuel_type", "Fuel type of the generator", None, "string", ColumnType.METADATA),
            ColumnMetadata("generator_name", "Name of the generator", None, "string", ColumnType.IDENTIFIER),
            ColumnMetadata("ons_id", "ONS ID of the generator", None, "string", ColumnType.IDENTIFIER),
            ColumnMetadata("ceg", "ONS CEG ID of the generator", None, "string", ColumnType.METADATA),
            ColumnMetadata("installed_capacity", "Installed capacity of the power plant", "MW", "float", ColumnType.DATA),
            ColumnMetadata("operational_availability", "Operational availability of the plant", "MW", "float", ColumnType.DATA),
            ColumnMetadata("synchronized_availability", "Synchronized operational availability", "MW", "float", ColumnType.DATA),
            ],
        )

        self._registry["ons_power_plant_hourly_generation"] = TableMetadata(
            table_name="ons_power_plant_hourly_generation",
            organization="ONS",
            data_name="Power Plant Hourly Generation",
            description="Hourly power generation data from individual power plants in the Brazilian National System Operator",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the generation observation", None, "datetime", ColumnType.DATETIME),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string", ColumnType.CATEGORY, values=SUBSYSTEMS),
                ColumnMetadata("state_code", "State code of the generator", None, "string", ColumnType.CATEGORY, values=STATE_CODES),
                ColumnMetadata("operation_mode", "Operation mode of the generator", None, "string", ColumnType.CATEGORY, values=OPERATION_MODES),
                ColumnMetadata("plant_type", "Type of the plant", None, "string", ColumnType.CATEGORY, values=PLANT_TYPES),
                ColumnMetadata("fuel_type", "Fuel type of the generator", None, "string", ColumnType.METADATA),
                ColumnMetadata("generator_name", "Name of the generator", None, "string", ColumnType.IDENTIFIER),
                ColumnMetadata("ons_id", "ONS ID of the generator", None, "string", ColumnType.IDENTIFIER),
                ColumnMetadata("ceg", "ONS CEG ID of the generator", None, "string", ColumnType.METADATA),
                ColumnMetadata("generation", "Forecasted power generation value", "MWavg", "float", ColumnType.DATA),
            ],
        )

    def get_metadata(self, table_name: str) -> Optional[TableMetadata]:
        return self._registry.get(table_name)

    def list_tables(self) -> List[str]:
        return list(self._registry.keys())

    def get_all_metadata(self) -> Dict[str, TableMetadata]:
        return self._registry.copy()


metadata_registry = MetadataRegistry()
