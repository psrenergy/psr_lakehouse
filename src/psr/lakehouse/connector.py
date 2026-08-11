import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from psr.lakehouse import auth
from psr.lakehouse.exceptions import LakehouseAuthError, LakehouseError


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

        # A deployment behind the load balancer needs a session cookie on every request; the
        # cached one is installed up front so a logged-in user is never asked again. The health
        # check below is exempt from authentication, so it passes either way and cannot be used
        # to tell whether we are logged in — that is discovered on the first real request.
        auth.load_session(self._base_url, self._session)

        try:
            response = self._session.get(f"{self._base_url}/health-check", timeout=10)
            if not response.json():
                raise LakehouseError("Health check failed: API returned a non-truthy response.")
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Health check failed: Unable to connect to API at {self._base_url}. {e}") from e

        self._is_initialized = True

    def login(self, base_url: str | None = None) -> None:
        """Sign in in a browser and cache the session, replacing any session already cached.

        Args:
            base_url: API base URL. Honoured even when the connector is already initialized —
                being a singleton, it may well be pointing somewhere else already.
        """
        target = base_url.rstrip("/") if base_url else None
        if not self._is_initialized or (target and target != getattr(self, "_base_url", None)):
            self.initialize(target or base_url)
        auth.login(self._base_url, session=self._session)

    def logout(self, base_url: str | None = None) -> bool:
        """Forget the cached session for this API, in this process and on disk.

        Deliberately does no initialization: throwing away a credential must not depend on the API
        being reachable, which is often exactly why someone is logging out.
        """
        target = base_url or getattr(self, "_base_url", None) or os.getenv("LAKEHOUSE_API_URL")
        if not target:
            raise LakehouseError(
                "No API URL to log out of. Pass base_url or set the LAKEHOUSE_API_URL environment variable."
            )

        if self._is_initialized:
            auth._clear_alb_cookies(self._session)
        return auth.clear_session(target.rstrip("/"))

    def _send(self, method: str, url: str, **kwargs) -> dict:
        """Send a request, logging in and retrying once if it was bounced to the login page.

        The load balancer answers an unauthenticated request with a redirect to Cognito, which
        `requests` follows — so what arrives here is a page of HTML from another host rather
        than an error status. `auth.bounced_to_idp` is what recognises that.
        """
        response = self._session.request(method, url, **kwargs)

        if auth.bounced_to_idp(response, self._base_url):
            auth.ensure_login(self._session, self._base_url)
            response = self._session.request(method, url, **kwargs)
            if auth.bounced_to_idp(response, self._base_url):
                raise LakehouseAuthError(
                    f"Still being redirected to the login page after logging in, requesting {url}."
                )

        if response.status_code == 403:
            # The load balancer let the request through, so the login worked; the application
            # itself refused the identity behind it.
            raise LakehouseAuthError(
                f"{self._base_url} rejected this account (HTTP 403). Access requires a verified "
                "@psr-inc.com email; run `psr-lakehouse login` to sign in as a different user."
            )

        response.raise_for_status()
        return response.json()

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
            return self._send("POST", url, json=json_body, params=params, timeout=timeout)
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
            return self._send("GET", url, params=params, timeout=60)
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
