# PSR Lakehouse 🏞️🏡

![Tests](https://github.com/psrenergy/psr_lakehouse/actions/workflows/ci.yml/badge.svg)  ![PyPI - Version](https://img.shields.io/pypi/v/psr-lakehouse?color=3dd13f) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://psrenergy.github.io/psr_lakehouse/)

A Python client library for accessing PSR's data lakehouse API, providing easy access to Brazilian energy market data including ANEEL, CCEE and ONS datasets.

## 📦 Installation

```bash
pip install psr-lakehouse
```

## ⚙️ Quick Start

Configure the API URL and AWS credentials:

```bash
export LAKEHOUSE_API_URL="https://api.example.com"
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"
```

Fetch data from the API:

```python
from psr.lakehouse import client

# Fetch CCEE spot price data
df = client.fetch_dataframe(
    table_name="ccee_spot_price",
    data_columns=["spot_price"],
    start_reference_date="2023-05-01",
    end_reference_date="2023-05-02",
    filters={"subsystem": "SOUTHEAST"},
)
print(df)
```

## 📚 Documentation

For complete documentation including advanced features, API reference, and examples, visit the [full documentation](https://psrenergy.github.io/psr_lakehouse/).

Features include:
- Data filtering and aggregation
- Temporal aggregation with datetime granularity
- Complex queries with table joins
- Schema discovery and exploration
- Custom ordering and timezone support

## 💬 Support

For questions or issues, please open an issue on the project repository.
