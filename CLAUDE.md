# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PSR Lakehouse is a Python client library for accessing Brazilian energy market data from PSR's data lakehouse. It provides convenient interfaces to CCEE (electricity market) and ONS (transmission operator) datasets.

## Development Commands

### Build and Package Management
- `uv sync` - Install/sync dependencies using uv package manager
- `uv build` - Build the package for distribution
- `uv publish` - Publish package to PyPI

### Code Quality
- `make lint` - Run ruff linting and formatting (includes `uv run ruff check . --fix` and `uv run ruff format .`)
- `uv run ruff check . --fix` - Run linting with auto-fixes
- `uv run ruff format .` - Format code

### Testing
- `make test` - Run all tests
- `uv run pytest -v -s` - Run tests with verbose output
- `uv run pytest tests/unit/test_ccee.py -v` - Run specific test file
- `uv run pytest tests/unit/test_ccee.py::test_function_name -v` - Run specific test function

## Architecture

### Core Components

**Singleton Pattern**: Both `Client` and `Connector` classes use singleton pattern to ensure single instances throughout the application.

**Database Layer**:
- `connector.py` - Handles AWS authentication and PostgreSQL connection management
- `client.py` - Provides high-level data access methods with automatic query building
- Uses SQLAlchemy for database connections and pandas for data manipulation

**Data Access**:
- `aliases/` - Contains domain-specific data access functions
- `aliases/ccee.py` - CCEE (electricity market) data functions like `spot_price()`
- `aliases/ons.py` - ONS (transmission operator) data functions like `stored_energy()` and `load_marginal_cost_weekly()`

**AWS Integration**:
- Uses boto3 for AWS services (RDS, Secrets Manager)
- Credentials from environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `POSTGRES_PASSWORD`
- Retrieves database connection details from AWS Secrets Manager

### Key Patterns

**Data Fetching**: All data access follows the pattern:
1. Use `client.fetch_dataframe()` with table name, index columns, and data columns
2. Automatic filtering by `reference_date` ranges and soft-delete handling (`deleted_at IS NULL`)
3. Results returned as pandas DataFrames with proper indexing

**Connection Management**: Database connections are lazy-loaded - `connector.initialize()` is called automatically when first database access occurs.

## Configuration

- **Python Version**: Requires Python 3.13+
- **Package Manager**: Uses `uv` instead of pip/poetry
- **Code Style**: Configured via `ruff.toml` - 120 character line length, double quotes, Python 3.13 target
- **Dependencies**: Core deps include boto3, pandas, psycopg, sqlalchemy

## Testing

Tests are located in `tests/unit/` with separate files for each alias module. Uses pytest framework with configuration in `conftest.py`.