import re

import pandas as pd

from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseError
from psr.lakehouse.metadata import get_model_name


class Client:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _build_query_data(self, model_name: str, columns: list[str]) -> list[str]:
        """Build query_data list with Model.column format."""
        return [f"{model_name}.{col}" for col in columns]

    def _build_query_filters(
        self,
        model_name: str,
        filters: dict | None,
        start_reference_date: str | None,
        end_reference_date: str | None,
    ) -> list[dict] | None:
        """Build query_filters list from parameters."""
        query_filters = []

        if filters:
            for col, value in filters.items():
                if value is not None:
                    query_filters.append(
                        {
                            "column": f"{model_name}.{col}",
                            "value": str(value),
                            "operator": "=",
                        }
                    )

        if start_reference_date:
            query_filters.append(
                {
                    "column": f"{model_name}.reference_date",
                    "value": start_reference_date,
                    "operator": ">=",
                }
            )

        if end_reference_date:
            query_filters.append(
                {
                    "column": f"{model_name}.reference_date",
                    "value": end_reference_date,
                    "operator": "<=",
                }
            )

        return query_filters if query_filters else None

    def _build_group_by(
        self,
        model_name: str,
        group_by: list[str] | None,
        aggregation_method: str | None,
        datetime_granularity: str | None = None,
    ) -> dict | None:
        """Build group_by clause."""
        if not group_by or not aggregation_method:
            return None

        return {
            "group_by_clause": [f"{model_name}.{col}" for col in group_by],
            "default_aggregation_method": aggregation_method,
            "datetime_granularity": datetime_granularity,
        }

    def _build_order_by(
        self,
        model_name: str,
        order_by: list[dict] | None,
    ) -> list[dict] | None:
        """Build order_by clause."""
        if not order_by:
            return None

        return [
            {
                "column": f"{model_name}.{item['column']}",
                "direction": item["direction"],
            }
            for item in order_by
        ]

    def _build_joins(
        self,
        joins: list[dict] | None,
    ) -> list[dict] | None:
        """Build joins clause."""
        if not joins:
            return None

        return joins

    def _fetch_all_pages(self, json_body: dict, page_size: int = 1000) -> list[dict]:
        """Fetch all pages of results."""
        all_data = []
        page = 1

        while True:
            response = connector.post(
                "/query/",
                json_body,
                params={"page": page, "page_size": page_size},
            )
            all_data.extend(response["data"])

            if not response["pagination"]["has_next"]:
                break
            page += 1

        return all_data

    def fetch_dataframe(
        self,
        table_name: str,
        indices_columns: list[str] | None = None,
        data_columns: list[str] | None = None,
        filters: dict | None = None,
        start_reference_date: str | None = None,
        end_reference_date: str | None = None,
        group_by: list[str] | None = None,
        datetime_granularity: str | None = None,
        order_by: list[dict] | None = None,
        aggregation_method: str | None = None,
        joins: list[dict] | None = None,
        output_timezone: str = "America/Sao_Paulo",
    ) -> pd.DataFrame:
        """
        Fetch data from the API and return as a pandas DataFrame.

        Args:
            table_name: Name of the table to query (e.g., "ccee_spot_price")
            indices_columns: Optional columns to use as DataFrame index. If not provided, DataFrame will use default integer index.
            data_columns: Optional data columns to fetch. If not provided along with indices_columns, all columns will be fetched.
            filters: Optional dict of column: value filters (equality)
            start_reference_date: Optional start date filter (inclusive)
            end_reference_date: Optional end date filter (exclusive)
            group_by: Optional list of columns to group by
            aggregation_method: Aggregation method (sum, avg, min, max) - required if group_by is set

        Returns:
            pandas DataFrame with the query results
        """
        # Validate group_by and aggregation_method
        if bool(group_by) ^ bool(aggregation_method is not None):
            raise LakehouseError("Both 'group_by' and 'aggregation_method' must be provided together.")

        if aggregation_method and aggregation_method not in ["", "sum", "avg", "min", "max"]:
            raise LakehouseError(
                f"Unsupported aggregation method '{aggregation_method}'. Supported: '', 'sum', 'avg', 'min', 'max'."
            )

        # Convert table name to model name
        model_name = get_model_name(table_name)

        final_indices = group_by if group_by else indices_columns

        # Combine all columns, ensuring no duplicates
        if final_indices and data_columns:
            all_columns = list(dict.fromkeys(final_indices + data_columns))
        elif final_indices:
            all_columns = final_indices
        elif data_columns:
            all_columns = data_columns
        else:
            all_columns = []

        # Build JSON request body
        json_body = {
            "query_data": self._build_query_data(model_name, all_columns),
            "output_timezone": output_timezone,
        }

        # Add optional fields
        query_filters = self._build_query_filters(model_name, filters, start_reference_date, end_reference_date)
        if query_filters:
            json_body["query_filters"] = query_filters

        group_by_clause = self._build_group_by(model_name, group_by, aggregation_method, datetime_granularity)
        if group_by_clause:
            json_body["group_by"] = group_by_clause

        order_by_clause = self._build_order_by(model_name, order_by)
        if order_by_clause:
            json_body["order_by"] = order_by_clause

        joins_clause = self._build_joins(joins)
        if joins_clause:
            json_body["joins"] = joins_clause

        return self.fetch_dataframe_from_query(json_body)

    def fetch_dataframe_from_query(self, json_body: dict, page_size: int = 1000) -> pd.DataFrame:
        """
        Fetch data from the API using a custom query JSON body and return as a pandas DataFrame.

        Args:
            json_body: JSON request body for the query

        Returns:
            pandas DataFrame with the query results
        """
        data = self._fetch_all_pages(json_body, page_size=page_size)
        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Convert datetime columns
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])

        # Set index if reference_date exists
        if "reference_date" in df.columns:
            df = df.set_index("reference_date")

        return df

    def _fetch_openapi_schema(self) -> dict:
        """Fetch OpenAPI schema from the API."""
        return connector.get("/openapi.json")["components"]["schemas"]

    def _get_enum_values(self, enum_reference: dict, defs: dict | None = None) -> list[str]:
        """Get enum values from OpenAPI schema."""
        ref = enum_reference["$ref"]

        # Handle local $defs references (e.g., #/$defs/Subsystem)
        defs_match = re.findall(r"^#/\$defs/(.+)$", ref)
        if defs_match and defs:
            enum_name = defs_match[0]
            if enum_name in defs and "enum" in defs[enum_name]:
                return defs[enum_name]["enum"]
            return []

        # Handle component schema references (e.g., #/components/schemas/Subsystem)
        schemas_match = re.findall(r"^#/components/schemas/(.+)$", ref)
        if not schemas_match:
            return []
        schemas = self._fetch_openapi_schema()
        enum_name = schemas_match[0]
        if enum_name not in schemas or "enum" not in schemas[enum_name]:
            return []
        return schemas[enum_name]["enum"]

    def get_schema(self, table_name: str) -> dict:
        """Get clean schema for a given table."""
        table_name = get_model_name(table_name)
        schemas = self._fetch_openapi_schema()
        model_schema = schemas[table_name]
        properties = model_schema["properties"]
        defs = model_schema.get("$defs", {})

        # Build clean schema
        clean_schema = {}
        for key, value in properties.items():
            field_info = {
                "type": self._extract_type(value),
                "nullable": self._is_nullable(value),
            }

            # Add description if present
            if "description" in value:
                field_info["description"] = value["description"]

            # Add title if present
            if "title" in value:
                field_info["title"] = value["title"]

            # Add format if present (e.g., date-time)
            if "format" in value:
                field_info["format"] = value["format"]

            # Handle enum values
            enum_values = None
            if "$ref" in value:
                enum_values = self._get_enum_values(value, defs)
            elif "anyOf" in value:
                for item in value["anyOf"]:
                    if "$ref" in item:
                        enum_values = self._get_enum_values(item, defs)
                        break
            elif "allOf" in value:
                for item in value["allOf"]:
                    if "$ref" in item:
                        enum_values = self._get_enum_values(item, defs)
                        break

            if enum_values:
                field_info["type"] = "enum"
                field_info["enum_values"] = enum_values

            clean_schema[key] = field_info

        return clean_schema

    def _extract_type(self, value: dict) -> str:
        """Extract the primary type from a field definition."""
        if "type" in value:
            return value["type"]
        elif "anyOf" in value:
            # Get first non-null type
            for item in value["anyOf"]:
                if item.get("type") != "null":
                    return item.get("type", "unknown")
            return "null"
        return "unknown"

    def _is_nullable(self, value: dict) -> bool:
        """Check if a field is nullable."""
        if "anyOf" in value:
            return any(item.get("type") == "null" for item in value["anyOf"])
        return False

    def list_tables(self) -> list[str]:
        """List all available tables in Lakehouse."""
        schemas = self._fetch_openapi_schema()

        # Filter out non-table schemas
        table_names = []
        for key, schema in schemas.items():
            # Skip enums (they have 'enum' field instead of 'properties')
            if "enum" in schema:
                continue

            # Skip schemas without properties
            if "properties" not in schema:
                continue

            # Check if it's a database model by looking for common model fields
            properties = schema.get("properties", {})

            # Database models typically have these fields
            has_model_fields = any(field in properties for field in ["id", "updated_at", "deleted_at"])

            # If it has model fields, it's likely a table
            if has_model_fields:
                table_names.append(key)

        return sorted(table_names)

    def get_table_columns(self, table_name: str) -> list[str]:
        """Get list of columns for a given table."""
        schema = self.get_schema(table_name)
        return list(schema.keys())


client = Client()
