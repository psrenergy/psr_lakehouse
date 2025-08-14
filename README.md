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

df = ccee.spot_price()
```

### ONS

```python
from psr.lakehouse import ons

df = ons.stored_energy(
    start_reference_date="2023-05-01 03:00:00",
    end_reference_date="2023-05-01 04:00:00",
)
```

## Support

For questions or issues, please open an issue on the project repository.