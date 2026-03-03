import os

import dotenv
import pytest

from psr.lakehouse import initialize

dotenv.load_dotenv()


@pytest.fixture(autouse=True, scope="session")
def init_connector():
    """Initialize connector with real credentials for integration tests."""
    api_url = os.getenv("LAKEHOUSE_API_URL")
    if not api_url:
        pytest.skip("LAKEHOUSE_API_URL not set — skipping integration tests")

    initialize(base_url=api_url)
