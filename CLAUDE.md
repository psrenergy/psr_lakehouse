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
- `connector.py` - HTTP client with health check validation on initialization
- `client.py` - High-level data access methods that build JSON query requests
- `auth.py` - Browser login for deployments behind the load balancer's Cognito authentication
- `__main__.py` - `psr-lakehouse login | logout | whoami`
- Uses `requests` for HTTP and `pandas` for data manipulation
- API URL from environment variable: `LAKEHOUSE_API_URL`

**Authentication** (`auth.py`):

The production API sits behind an ALB whose `authenticate-cognito` rule answers every
unauthenticated request with a `302` to the Cognito managed login page — which is why an
unauthenticated client sees HTML where it expected JSON. The only credential that load balancer
accepts is the `AWSELBAuthSessionCookie-*` pair it sets itself, at the end of a code flow whose
`redirect_uri` is fixed to `https://<host>/oauth2/idpresponse`. There is no bearer token or API
key to send. Signing in therefore happens **in a browser** — the only flow that works for every
account in a pool that also offers Google and passkeys — and `auth.py`'s whole job is getting the
resulting cookie into the client. It is cached in `~/.psr-lakehouse/session.json` (mode 0600).

- The hand-over works like pairing a device. `login` opens the browser at the lakehouse's
  `/auth/cli` page; the browser runs the whole Cognito flow on its own behalf and lands on that
  page holding a fresh session. The page (served by `lakehouse_server`'s `app/cli_auth/`) banks
  the session cookies behind a **one-time code** (10 minutes, single use) and shows the code;
  the user pastes it into the terminal and `_redeem_code` spends it at `POST /auth/cli/token` —
  reachable without a session, like `/health-check` — for the cookies plus the signed-in email.
- `_paste_cookie` is the fallback whenever the code cannot be redeemed (an old server, a load
  balancer missing the redeem endpoint's forwarding rule): `AWSELBAuthSessionCookie-0` copied
  out of the browser's devtools by hand.
- `connector._send()` recognises the bounce by comparing the host of the *final* URL against
  `base_url` — `requests` follows the redirect, so the status code alone does not reveal it.
  On a bounce it logs in and retries the request once.
- `/health-check` is exempt from authentication on the ALB, so `initialize()` succeeds whether
  or not there is a session; the state is only discovered on the first real request.
- No unattended login is possible (a browser is required); jobs reuse a session logged in
  interactively, via `LAKEHOUSE_SESSION_FILE`. `LAKEHOUSE_AUTO_LOGIN=0` disables the prompt.
- The redeem endpoint answers with the account's email, which is cached alongside the cookies —
  `whoami` reports who is logged in as well as whether the session is still valid.
- Server side: `lakehouse_server`'s `app/core/alb_auth.py` additionally requires a **verified**
  email in an allowed domain (`psr-inc.com`), answering `403` otherwise.

**Metadata**:
- `metadata.py` - Contains `get_model_name()` function to convert table names to API model names
- Handles uppercase prefixes (ONS, CCEE) in model name conversion

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
- **Dependencies**: Core deps include pandas, requests

## Testing

Tests are located in `tests/unit/` using pytest with HTTP mocking via `responses` library:
- `test_client.py` - Tests for Client class (fetch_dataframe, schema methods)
- `test_connector.py` - Tests for Connector class (HTTP requests, initialization)
- `test_metadata.py` - Tests for model name conversion

Test configuration in `conftest.py` sets up mock API URL environment variable.
