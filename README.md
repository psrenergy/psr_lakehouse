<div align="center">

<picture>

  <source media="(prefers-color-scheme: light)" srcset="./docs/_static/img/lakehouse_vertical_light.png">
  <source media="(prefers-color-scheme: dark)" srcset="./docs/_static/img/lakehouse_vertical_dark.png">
  <img height="200" alt="QARBoM.jl logo">
  
</picture>
<br>

![Tests](https://github.com/psrenergy/psr_lakehouse/actions/workflows/ci.yml/badge.svg)  ![PyPI - Version](https://img.shields.io/pypi/v/psr-lakehouse?color=3dd13f) [![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://psrenergy.github.io/psr_lakehouse/)


</div>

# PSR Lakehouse 🏞️🏡


A Python client library for accessing PSR's data lakehouse API, providing easy access to Brazilian energy market data including ANEEL, CCEE and ONS datasets.

## 📦 Installation

```bash
pip install psr-lakehouse
```

## ⚙️ Quick Start

Configure the API URL:

```bash
export LAKEHOUSE_API_URL="https://api.example.com"
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
