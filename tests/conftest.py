import os

import pytest
import responses

# Set environment variables for testing
os.environ["LAKEHOUSE_API_URL"] = "https://test-api.example.com"


@pytest.fixture
def mock_api():
    """Fixture to mock HTTP requests to the API."""
    with responses.RequestsMock() as rsps:
        yield rsps
