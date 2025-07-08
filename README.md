# PSR Lakehouse 🏞️🏡

A Python client library for accessing PSR's data lakehouse, providing easy access to Brazilian energy market data including CCEE and ONS datasets.

## Installation

```bash
pip install psr-lakehouse
```

## Examples

### CCEE

```python
from psr.lakehouse import ccee

# Get ccee spot prices
spot_prices = ccee.spot_price(
    filters = {"subsystem": "SE"},
    start_reference_date="2024-01-01",
    end_reference_date="2024-12-31"
)
```

### ONS

```python
from psr.lakehouse import ons

# Get ons maximum stored energy
max_energy = ons.max_stored_energy(
    filters = {"subsystem": "SE"},
    start_reference_date = "2024-01-01"
)

# Get ons verified stored energy in MW/month
verified_energy = ons.verified_stored_energy_mwmonth(
    filters = {"subsystem": "NE"}
)

# Get ons verified stored energy as percentage
energy_percentage = ons.verified_stored_energy_percentage()
```

## Support

For questions or issues, please open an issue on the project repository.