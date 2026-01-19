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

### Get Table Columns

```python
columns_df = client.get_table_columns("ccee_spot_price")
print(columns_df)
#              name       type  nullable  primary_key
# 0  reference_date  TIMESTAMP     False         True
# 1       subsystem    VARCHAR     False         True
# 2      spot_price      FLOAT     False        False
```

### Get Full Schema

```python
# Get schema for a specific model
schema = client.get_model_schema("CCEESpotPrice")
print(schema)

# Get schema for all models
all_schemas = client.get_schema()
```

## 📖 API Reference

### `client.fetch_dataframe()`

Fetch data from the API and return as a pandas DataFrame.

**Parameters:**
- `table_name` (str): Name of the table to query (e.g., "ccee_spot_price")
- `indices_columns` (list[str]): Columns to use as DataFrame index
- `data_columns` (list[str]): Data columns to fetch
- `filters` (dict, optional): Column filters as `{column: value}` for equality
- `start_reference_date` (str, optional): Start date filter (inclusive)
- `end_reference_date` (str, optional): End date filter (exclusive)
- `group_by` (list[str], optional): Columns to group by
- `aggregation_method` (str, optional): Aggregation method (`sum`, `avg`, `min`, `max`)

**Returns:** `pandas.DataFrame`

### `client.list_tables()`

List all available table names.

**Returns:** `list[str]`

### `client.list_models()`

List all available API model names.

**Returns:** `list[str]`

### `client.get_table_columns(table_name)`

Get column information for a specific table.

**Parameters:**
- `table_name` (str): Snake_case table name

**Returns:** `pandas.DataFrame` with columns: name, type, nullable, primary_key, description

### `client.get_model_schema(model_name)`

Get schema information for a specific model.

**Parameters:**
- `model_name` (str): API model name (e.g., "CCEESpotPrice")

**Returns:** `dict` with model_name, table_name, and columns list

### `client.get_schema()`

Get schema information for all available models.

**Returns:** `dict` with model names as keys and schema info as values

## 💬 Support

For questions or issues, please open an issue on the project repository.
