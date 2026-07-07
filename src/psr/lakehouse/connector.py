import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from psr.lakehouse.exceptions import LakehouseError


class Connector:
    _instance = None

    _is_initialized: bool = False
    _base_url: str
    _session: requests.Session

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _create_session() -> requests.Session:
        """Create a session with keep-alive and retries on transient server errors."""
        session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=Retry(
                total=3,
                backoff_factor=1,
                status_forcelist=[502, 503, 504],
                allowed_methods=["GET", "POST"],
            )
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def initialize(
        self,
        base_url: str | None = None,
    ):
        """
        Initialize the connector with API URL.

        Args:
            base_url: API base URL. Defaults to LAKEHOUSE_API_URL environment variable.
        """
        # Get base URL from parameter or environment variable
        self._base_url = base_url or os.getenv("LAKEHOUSE_API_URL")
        if not self._base_url:
            raise LakehouseError(
                "API base URL not provided. Set LAKEHOUSE_API_URL environment variable or pass base_url parameter."
            )
        self._base_url = self._base_url.rstrip("/")

        self._session = self._create_session()

        try:
            response = self._session.get(f"{self._base_url}/health-check", timeout=10)
            if not response.json():
                raise LakehouseError("Health check failed: API returned a non-truthy response.")
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Health check failed: Unable to connect to API at {self._base_url}. {e}") from e

        self._is_initialized = True

    def post(self, endpoint: str, json_body: dict, params: dict | None = None, timeout: int = 600) -> dict:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint path (e.g., "/query/")
            json_body: JSON request body
            params: Optional query parameters
            timeout: Request timeout in seconds (default: 600)

        Returns:
            JSON response as dictionary

        Raises:
            LakehouseError: If the request fails
        """
        if not self._is_initialized:
            self.initialize()

        url = f"{self._base_url}{endpoint}"

        try:
            response = self._session.post(
                url,
                json=json_body,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise LakehouseError(self._format_http_error(e, url)) from e
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Request to {url} failed: {e}") from e

    def get(self, endpoint: str, params: dict | None = None) -> dict:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint path (e.g., "/query/schema")
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            LakehouseError: If the request fails
        """
        if not self._is_initialized:
            self.initialize()

        url = f"{self._base_url}{endpoint}"

        try:
            response = self._session.get(
                url,
                params=params,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise LakehouseError(self._format_http_error(e, url)) from e
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Request to {url} failed: {e}") from e

    @staticmethod
    def _format_http_error(error: requests.exceptions.HTTPError, url: str) -> str:
        """Format an HTTP error into a concise, readable message."""
        status_code = error.response.status_code
        reason = error.response.reason

        # Try to extract a JSON error detail from the response
        try:
            detail = error.response.json()
            if isinstance(detail, dict) and "detail" in detail:
                detail = detail["detail"]
            return f"HTTP {status_code} {reason} for {url}: {detail}"
        except Exception:
            pass

        return f"HTTP {status_code} {reason} for {url}"


connector = Connector()
