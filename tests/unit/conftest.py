import os

import pytest
import responses


@pytest.fixture(autouse=True)
def setup_unit_test():
    """Set mock API URL and reset connector state for unit tests."""
    from psr.lakehouse.connector import connector

    original_url = os.environ.get("LAKEHOUSE_API_URL")
    os.environ["LAKEHOUSE_API_URL"] = "https://test-api.example.com"

    connector._is_initialized = False
    connector._base_url = None
    connector._auth = None

    yield

    # Restore original env
    if original_url is None:
        os.environ.pop("LAKEHOUSE_API_URL", None)
    else:
        os.environ["LAKEHOUSE_API_URL"] = original_url


@pytest.fixture
def mock_api():
    """Fixture to mock HTTP requests to the API."""
    with responses.RequestsMock() as rsps:
        yield rsps
