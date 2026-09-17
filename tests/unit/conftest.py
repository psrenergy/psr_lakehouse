import os

import pytest
import responses


@pytest.fixture(autouse=True)
def setup_unit_test():
    """Set mock API URL and reset connector state for unit tests."""
    from psr.lakehouse.connector import connector

    original_url = os.environ.get("LAKEHOUSE_API_URL")
    original_token = os.environ.get("LAKEHOUSE_PAT")
    os.environ["LAKEHOUSE_API_URL"] = "https://test-api.example.com"
    os.environ["LAKEHOUSE_PAT"] = "psr_test_token"

    connector._is_initialized = True
    connector._base_url = "https://test-api.example.com"
    connector._session = connector._create_session()
    connector._session.headers["Authorization"] = "Bearer psr_test_token"
    connector._identity = None
    # The missing-token notice is printed once per process; reset it so each
    # test sees it rather than only the first one to run.
    type(connector)._warned_about_missing_pat = False

    yield

    # Restore original env
    for name, original in (("LAKEHOUSE_API_URL", original_url), ("LAKEHOUSE_PAT", original_token)):
        if original is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = original


@pytest.fixture
def mock_api():
    """Fixture to mock HTTP requests to the API."""
    with responses.RequestsMock() as rsps:
        yield rsps
