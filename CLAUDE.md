# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PSR Lakehouse is a Python client library for accessing Brazilian energy market data from PSR's data lakehouse API. It provides convenient interfaces to ANEEL, CCEE (electricity market) and ONS (transmission operator) datasets via HTTP API.

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
- `uv run pytest tests/unit/test_client.py -v` - Run specific test file
- `uv run pytest tests/unit/test_client.py::TestFetchDataframe -v` - Run specific test class

## Architecture

### Core Components

**Singleton Pattern**: Both `Client` and `Connector` classes use singleton pattern to ensure single instances throughout the application.

**HTTP Layer**:
- `connector.py` - HTTP client with AWS IAM authentication (AWS4Auth)
- `client.py` - High-level data access methods that build JSON query requests
- Uses `requests` for HTTP and `pandas` for data manipulation

**Metadata**:
- `metadata.py` - Contains `get_model_name()` function to convert table names to API model names
- Handles uppercase prefixes (ONS, CCEE) in model name conversion

**AWS Integration**:
- Uses `requests-aws4auth` for API Gateway IAM authentication
- Uses `boto3` for AWS credential resolution
- Credentials from environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- API URL from environment variable: `LAKEHOUSE_API_URL`

### Key Patterns

**Data Fetching**: All data access follows the pattern:
1. Use `client.fetch_dataframe()` with table name, index columns, and data columns
2. Client converts table name to model name and builds JSON query request
3. Automatic pagination - fetches all pages and concatenates results
4. Results returned as pandas DataFrames with proper MultiIndex

**Schema Discovery**:
- `client.list_tables()` - List all available table names
- `client.get_table_columns(table_name)` - Get column info as DataFrame
- `client.get_schema()` - Get full schema for all models

**Connection Management**: HTTP connector is lazy-initialized - `connector.initialize()` is called automatically on first API request.

## Configuration

- **Python Version**: Requires Python 3.13+
- **Package Manager**: Uses `uv` instead of pip/poetry
- **Code Style**: Configured via `ruff.toml` - 120 character line length, double quotes, Python 3.13 target
- **Dependencies**: Core deps include boto3, pandas, requests, requests-aws4auth

## Testing

Tests are located in `tests/unit/` using pytest with HTTP mocking via `responses` library:
- `test_client.py` - Tests for Client class (fetch_dataframe, schema methods)
- `test_connector.py` - Tests for Connector class (HTTP requests, initialization)
- `test_metadata.py` - Tests for model name conversion

Test configuration in `conftest.py` sets up mock API URL environment variable.
