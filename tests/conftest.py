import os

import pytest
import responses

# Set environment variables for testing
os.environ["LAKEHOUSE_API_URL"] = "https://test-api.example.com"


@pytest.fixture(autouse=True)
def reset_connector():
    """Reset connector state before each test."""
    from psr.lakehouse import connector

    connector._is_initialized = False
    connector._base_url = None
    connector._auth = None
    yield


@pytest.fixture
def mock_api():
    """Fixture to mock HTTP requests to the API."""
    with responses.RequestsMock() as rsps:
        yield rsps
