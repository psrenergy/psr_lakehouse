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
                    "operator": "<",
                }
            )

        return query_filters if query_filters else None

    def _build_group_by(
        self,
        model_name: str,
        group_by: list[str] | None,
        aggregation_method: str | None,
    ) -> dict | None:
        """Build group_by clause."""
        if not group_by or not aggregation_method:
            return None

        return {
            "group_by_clause": [f"{model_name}.{col}" for col in group_by],
            "default_aggregation_method": aggregation_method,
        }

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
        aggregation_method: str | None = None,
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

        # Handle group_by with reference_date
        if group_by and "reference_date" not in group_by:
            group_by = group_by + ["reference_date"]

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
            "output_timezone": "America/Sao_Paulo",
        }

        # Add optional fields
        query_filters = self._build_query_filters(model_name, filters, start_reference_date, end_reference_date)
        if query_filters:
            json_body["query_filters"] = query_filters

        group_by_clause = self._build_group_by(model_name, group_by, aggregation_method)
        if group_by_clause:
            json_body["group_by"] = group_by_clause

        # Fetch all pages
        data = self._fetch_all_pages(json_body)

        # Convert to DataFrame
        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Convert datetime columns
        if "reference_date" in df.columns:
            df["reference_date"] = pd.to_datetime(df["reference_date"])

        # Set index
        if final_indices:
            existing_indices = [col for col in final_indices if col in df.columns]
            if existing_indices:
                df = df.set_index(existing_indices)
        elif "reference_date" in df.columns:
            # If no index specified but reference_date exists, use it as index
            df = df.set_index("reference_date")

        return df

    def get_schema(self) -> dict:
        """
        Get schema information for all available models from the API.

        Returns:
            Dictionary with model names as keys and schema info as values.
            Each model contains table_name and columns list with:
            - name: Column name
            - type: Column data type
            - nullable: Whether column is nullable
            - primary_key: Whether column is a primary key
            - description: Column description (if available)
            - enum_values: Possible values for enum columns (if applicable)
        """
        return connector.get("/query/schema")

    def get_model_schema(self, model_name: str) -> dict:
        """
        Get schema information for a specific model from the API.

        Args:
            model_name: The API model name (e.g., "CCEESpotPrice", "ONSEnergyLoadDaily")

        Returns:
            Dictionary with model_name, table_name, and columns list.
        """
        return connector.get(f"/query/schema/{model_name}")

    def list_models(self) -> list[str]:
        """
        List all available model names from the API.

        Returns:
            List of model names (e.g., ["CCEESpotPrice", "ONSEnergyLoadDaily", ...])
        """
        schema = self.get_schema()
        return sorted(schema.keys())

    def list_tables(self) -> list[str]:
        """
        List all available table names from the API.

        Returns:
            List of table names (e.g., ["ccee_spot_price", "ons_energy_load_daily", ...])
        """
        schema = self.get_schema()
        return sorted([info["table_name"] for info in schema.values()])

    def get_table_columns(self, table_name: str) -> pd.DataFrame:
        """
        Get column information for a specific table from the API.

        Args:
            table_name: Snake_case table name (e.g., "ccee_spot_price") or final API model name (e.g., "CCEESpotPrice")

        Returns:
            DataFrame with column information (name, type, nullable, primary_key, description)
        """
        model_name = get_model_name(table_name)
        schema = self.get_model_schema(model_name)
        return pd.DataFrame(schema["columns"])


client = Client()
