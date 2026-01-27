import os

import boto3
import requests
from requests_aws4auth import AWS4Auth

from psr.lakehouse.exceptions import LakehouseError


class Connector:
    _instance = None

    _region_name = "us-east-1"
    _is_initialized: bool = False
    _base_url: str
    _auth: AWS4Auth | None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        base_url: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        region: str | None = None,
    ):
        """
        Initialize the connector with API URL and AWS credentials.

        Args:
            base_url: API base URL. Defaults to LAKEHOUSE_API_URL environment variable.
            aws_access_key_id: AWS access key. Defaults to AWS_ACCESS_KEY_ID env var or boto3 session.
            aws_secret_access_key: AWS secret key. Defaults to AWS_SECRET_ACCESS_KEY env var or boto3 session.
            region: AWS region. Defaults to us-east-1.
        """
        # Get base URL from parameter or environment variable
        self._base_url = base_url or os.getenv("LAKEHOUSE_API_URL")
        if not self._base_url:
            raise LakehouseError(
                "API base URL not provided. Set LAKEHOUSE_API_URL environment variable or pass base_url parameter."
            )
        self._base_url = self._base_url.rstrip("/")

        # Get region
        self._region_name = region or os.getenv("AWS_REGION", "us-east-1")

        # Get AWS credentials
        access_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
        secret_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

        # If credentials not provided explicitly, try to get from boto3 session
        if not access_key or not secret_key:
            try:
                session = boto3.Session()
                credentials = session.get_credentials()
                if credentials:
                    access_key = credentials.access_key
                    secret_key = credentials.secret_key
            except Exception:
                pass

        # Set up AWS IAM authentication if credentials are available
        if access_key and secret_key:
            self._auth = AWS4Auth(
                access_key,
                secret_key,
                self._region_name,
                "execute-api",  # Service name for API Gateway
            )
        else:
            self._auth = None

        self._is_initialized = True

    def post(self, endpoint: str, json_body: dict, params: dict | None = None) -> dict:
        """
        Make a POST request to the API.

        Args:
            endpoint: API endpoint path (e.g., "/query/")
            json_body: JSON request body
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
            response = requests.post(
                url,
                json=json_body,
                params=params,
                auth=self._auth,
                timeout=300,
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
                auth=self._auth,
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
