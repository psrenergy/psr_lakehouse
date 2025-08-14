from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ColumnMetadata:
    name: str
    description: str
    unit: Optional[str] = None
    data_type: Optional[str] = None


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
                ColumnMetadata("reference_date", "Date and time of the price observation", None, "datetime"),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string"),
                ColumnMetadata("spot_price", "Electricity spot price", "R$/MWh", "float"),
            ],
        )

        # ONS Tables
        self._registry["ons_stored_energy"] = TableMetadata(
            table_name="ons_stored_energy",
            organization="ONS",
            data_name="Stored Energy",
            description="Reservoir stored energy levels by subsystem from the Brazilian National System Operator",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the observation", None, "datetime"),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string"),
                ColumnMetadata("max_stored_energy", "Maximum storage capacity", "MWmonth", "float"),
                ColumnMetadata("verified_stored_energy_mwmonth", "Verified stored energy amount", "MWmonth", "float"),
                ColumnMetadata(
                    "verified_stored_energy_percentage",
                    "Verified stored energy as percentage of capacity",
                    "%",
                    "float",
                ),
            ],
        )

        self._registry["ons_load_marginal_cost_weekly"] = TableMetadata(
            table_name="ons_load_marginal_cost_weekly",
            organization="ONS",
            data_name="Load Marginal Cost Weekly",
            description="Weekly marginal cost of load by subsystem and load segment from the Brazilian National System Operator",
            columns=[
                ColumnMetadata("reference_date", "Date and time of the weekly period", None, "datetime"),
                ColumnMetadata("subsystem", "Electrical subsystem identifier", None, "string"),
                ColumnMetadata("average", "Average marginal cost across all load segments", "R$/MWh", "float"),
                ColumnMetadata("light_load_segment", "Marginal cost during light load periods", "R$/MWh", "float"),
                ColumnMetadata("medium_load_segment", "Marginal cost during medium load periods", "R$/MWh", "float"),
                ColumnMetadata("heavy_load_segment", "Marginal cost during heavy load periods", "R$/MWh", "float"),
            ],
        )

    def get_metadata(self, table_name: str) -> Optional[TableMetadata]:
        return self._registry.get(table_name)

    def list_tables(self) -> List[str]:
        return list(self._registry.keys())

    def get_all_metadata(self) -> Dict[str, TableMetadata]:
        return self._registry.copy()


metadata_registry = MetadataRegistry()
