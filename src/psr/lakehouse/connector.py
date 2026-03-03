import os

import requests

from psr.lakehouse.exceptions import LakehouseError


class Connector:
    _instance = None

    _is_initialized: bool = False
    _base_url: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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

        try:
            response = requests.get(f"{self._base_url}/health-check", timeout=10)
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
            response = requests.post(
                url,
                json=json_body,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise LakehouseError(f"API request failed: {e}. Details: {error_detail}") from e
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"API request failed: {e}") from e

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
            response = requests.get(
                url,
                params=params,
                timeout=60,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            try:
                error_detail = e.response.json()
            except Exception:
                error_detail = e.response.text
            raise LakehouseError(f"API request failed: {e}. Details: {error_detail}") from e
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"API request failed: {e}") from e


connector = Connector()
