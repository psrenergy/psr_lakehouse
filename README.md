# PSR Lakehouse 🏞️🏡

A Python client library for accessing PSR's data lakehouse API, providing easy access to Brazilian energy market data including ANEEL, CCEE and ONS datasets.

## 📦 Installation

```bash
pip install psr-lakehouse
```

## ⚙️ Configuration

Set the API URL via environment variable:

```bash
export LAKEHOUSE_API_URL="https://api.example.com"
```

For AWS IAM authentication, configure your AWS credentials:

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

Or initialize programmatically:

```python
from psr.lakehouse import initialize

initialize(
    base_url="https://api.example.com",
    aws_access_key_id="your-access-key",
    aws_secret_access_key="your-secret-key",
    region="us-east-1",
)
```

## 🚀 Usage

### Fetching Data

```python
from psr.lakehouse import client

# Fetch CCEE spot price data
df = client.fetch_dataframe(
    table_name="ccee_spot_price",
    indices_columns=["reference_date", "subsystem"],
    data_columns=["spot_price"],
    start_reference_date="2023-05-01",
    end_reference_date="2023-05-02",
)
print(df)
```

### Filtering Data

```python
# Filter by subsystem
df = client.fetch_dataframe(
    table_name="ons_stored_energy_subsystem",
    indices_columns=["reference_date", "subsystem"],
    data_columns=["max_stored_energy", "verified_stored_energy_percentage"],
    start_reference_date="2023-05-01",
    end_reference_date="2023-05-02",
    filters={"subsystem": "SOUTHEAST"},
)
```

### Aggregating Data

```python
# Group by subsystem and calculate average
df = client.fetch_dataframe(
    table_name="ccee_spot_price",
    indices_columns=["reference_date", "subsystem"],
    data_columns=["spot_price"],
    start_reference_date="2023-01-01",
    end_reference_date="2023-02-01",
    group_by=["subsystem"],
    aggregation_method="avg",
)

# Aggregate hourly data to daily with datetime granularity
df = client.fetch_dataframe(
    table_name="ons_power_plant_hourly_generation",
    data_columns=["plant_type", "generation"],
    start_reference_date="2025-01-01",
    end_reference_date="2025-01-31",
    group_by=["reference_date", "plant_type"],
    aggregation_method="sum",
    datetime_granularity="day",  # Aggregate to daily level
)
```

### Ordering Results

```python
# Order results by multiple columns
df = client.fetch_dataframe(
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
```

### Advanced Queries with Joins

```python
# Use fetch_dataframe_from_query for complex queries with joins
df = client.fetch_dataframe_from_query({
    "query_data": [
        "ONSEnergyLoadDaily.reference_date",
        "ONSEnergyLoadDaily.subsystem",
        "ONSEnergyLoadDaily.energy_load",
        "ONSInflowEnergySubsystem.gross_inflow_energy_mwavg",
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
})
```

## 🔍 Schema Discovery

### List Available Tables

```python
tables = client.list_tables()
print(tables)
# ['ccee_spot_price', 'ons_energy_load_daily', 'ons_stored_energy_subsystem', ...]
```

### List Available Models

```python
models = client.list_models()
print(models)
# ['CCEESpotPrice', 'ONSEnergyLoadDaily', 'ONSStoredEnergySubsystem', ...]
```

### Get Table Schema

```python
# Get schema for a specific table
schema = client.get_schema("ccee_spot_price")
print(schema)
# {
#     'id': {'type': 'integer', 'nullable': True, 'title': 'Id'},
#     'reference_date': {
#         'type': 'string',
#         'nullable': False,
#         'format': 'date-time',
#         'title': 'Reference Date',
#         'description': 'Timestamp of the spot price'
#     },
#     'subsystem': {
#         'type': 'enum',
#         'nullable': True,
#         'description': 'Subsystem identifier',
#         'enum_values': ['NORTE', 'NORDESTE', 'SUDESTE', 'SUL', 'SISTEMA INTERLIGADO NACIONAL']
#     },
#     'spot_price': {
#         'type': 'number',
#         'nullable': False,
#         'title': 'Spot Price',
#         'description': 'Spot price in R$/MWh'
#     }
# }
```

## 📖 API Reference

### `client.fetch_dataframe()`

Fetch data from the API and return as a pandas DataFrame.

**Parameters:**
- `table_name` (str): Name of the table to query (e.g., "ccee_spot_price")
- `indices_columns` (list[str], optional): Columns to use as DataFrame index
- `data_columns` (list[str], optional): Data columns to fetch
- `filters` (dict, optional): Column filters as `{column: value}` for equality
- `start_reference_date` (str, optional): Start date filter (inclusive)
- `end_reference_date` (str, optional): End date filter (exclusive)
- `group_by` (list[str], optional): Columns to group by
- `aggregation_method` (str, optional): Aggregation method (`sum`, `avg`, `min`, `max`)
- `datetime_granularity` (str, optional): Temporal aggregation level (`hour`, `day`, `week`, `month`)
- `order_by` (list[dict], optional): Sort order as list of `{"column": str, "direction": "asc"|"desc"}`
- `output_timezone` (str, optional): Output timezone (default: "America/Sao_Paulo")

**Returns:** `pandas.DataFrame`

### `client.fetch_dataframe_from_query()`

Fetch data using a custom JSON query body for advanced features like joins.

**Parameters:**
- `json_body` (dict): JSON request body with query specification
- `page_size` (int, optional): Results per page (default: 1000)

**Query body structure:**
- `query_data` (list[str]): Columns to fetch in "ModelName.column" format
- `query_filters` (list[dict], optional): Filters with `column`, `operator`, `value`
- `group_by` (dict, optional): Group by clause with `group_by_clause`, `default_aggregation_method`, `datetime_granularity`
- `order_by` (list[dict], optional): Sort order with `column` and `direction`
- `joins` (list[dict], optional): Join specifications with `join_model`, `join_filters`, `is_outer_join`

**Returns:** `pandas.DataFrame`

### `client.list_tables()`

List all available table names.

**Returns:** `list[str]`

### `client.list_models()`

List all available API model names.

**Returns:** `list[str]`

### `client.get_schema(table_name)`

Get detailed schema information for a specific table, including field types, nullability, formats, and enum values.

**Parameters:**
- `table_name` (str): Snake_case table name (e.g., "ccee_spot_price")

**Returns:** `dict` with field names as keys and field metadata as values. Each field contains:
- `type` (str): Field type (`string`, `integer`, `number`, `enum`, etc.)
- `nullable` (bool): Whether the field accepts null values
- `title` (str, optional): Human-readable field name
- `description` (str, optional): Field description
- `format` (str, optional): Format specification (e.g., `date-time`)
- `enum_values` (list[str], optional): Allowed values for enum fields

## 💬 Support

For questions or issues, please open an issue on the project repository.
