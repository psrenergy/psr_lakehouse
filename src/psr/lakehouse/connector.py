import os
import sys

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from psr.lakehouse.exceptions import LakehouseAuthError, LakehouseError


class Connector:
    _instance = None

    _is_initialized: bool = False
    _base_url: str
    _session: requests.Session
    _identity: dict | None = None
    _pat: str | None = None
    _warned_about_missing_pat: bool = False

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
                # 503 is retried because the usual cause is transient. A 503 that
                # persists past the backoff is a server-side misconfiguration and
                # is reported as such rather than as a bad token. 401 and 403 are
                # deliberately absent: a bad token must fail fast.
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
        pat: str | None = None,
    ):
        """
        Initialize the connector with the API URL and a personal access token.

        Args:
            base_url: API base URL. Defaults to LAKEHOUSE_API_URL environment variable.
            pat: PSR personal access token (`psr_...`). Generate one at
                https://cockpit.psr-inc.com. Prefer leaving this unset and using
                the LAKEHOUSE_PAT environment variable: a token written literally
                into this call is printed in full by any traceback that passes
                through the line, since Python renders the source of every frame.
                Passing a token read from somewhere else - `os.environ`, a secret
                manager - is fine, because the traceback shows the expression
                rather than its value.

        Raises:
            LakehouseAuthError: If the token is rejected, or if its owner holds
                no active Lakehouse plan.
            LakehouseError: If the API URL is missing or the API is unreachable.

        Note:
            A token is not yet mandatory. Without one this warns and carries on,
            so existing scripts keep running until the API starts requiring it.
        """
        # Get base URL from parameter or environment variable
        self._base_url = base_url or os.getenv("LAKEHOUSE_API_URL")
        if not self._base_url:
            raise LakehouseError(
                "API base URL not provided. Set LAKEHOUSE_API_URL environment variable or pass base_url parameter."
            )
        self._base_url = self._base_url.rstrip("/")

        self._pat = pat or os.getenv("LAKEHOUSE_PAT")

        self._session = self._create_session()
        if self._pat:
            # Set on the session rather than per call, so no request can be
            # added later that forgets to carry it.
            self._session.headers["Authorization"] = f"Bearer {self._pat}"
        else:
            # Deliberately a warning and not an error, for now. The API does not
            # reject anonymous queries yet, and turning this into an exception
            # before it does would break every existing script for no benefit -
            # the upgrade window is the whole point. It becomes an error once the
            # API is gated; until then the job of this message is to make sure
            # nobody is surprised on that day.
            # Printed rather than raised through `warnings`, whose formatting
            # prefixes every message with the file and line that triggered it -
            # "<stdin-1>:1:" in a REPL, which is noise to the analyst this is
            # addressed to. Once per process: it is a nudge, not a nag.
            if not Connector._warned_about_missing_pat:
                Connector._warned_about_missing_pat = True
                print(
                    "psr-lakehouse: no personal access token configured; querying the PSR "
                    "Lakehouse is becoming token-only.\n"
                    "               Generate one at https://cockpit.psr-inc.com and set it "
                    "in the LAKEHOUSE_PAT environment variable.",
                    file=sys.stderr,
                )

        # Reachability first, with no token involved, so "the API is down" and
        # "your token is bad" cannot be reported as each other.
        try:
            response = self._session.get(f"{self._base_url}/health-check", timeout=10)
            if not response.json():
                raise LakehouseError("Health check failed: API returned a non-truthy response.")
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Health check failed: Unable to connect to API at {self._base_url}. {e}") from e

        # Then the token, once, here. Without this the first failure of a bad
        # token is whichever fetch_dataframe happens to run first, which in a
        # notebook is often minutes of work later. Skipped when there is no
        # token: against a gated API it would only 401, and against an ungated
        # one there is nothing to resolve.
        if self._pat:
            self._identity = self.get("/query/whoami", _skip_init_check=True)
            # Greeting the person by name is the shortest way to answer the two
            # questions a token raises - is it working, and whose is it. Reading
            # the wrong name here is how someone catches a stale LAKEHOUSE_PAT
            # before a day's analysis is attributed to a colleague.
            name = self._identity.get("full_name") or self._identity.get("email") or "back"
            print(f"Welcome, {name}!", file=sys.stderr)

        self._is_initialized = True

    def whoami(self) -> dict:
        """Return who the configured token belongs to, and the plan it carries.

        Resolved once at initialize() and held, so this is free to call. It is
        the answer to "am I about to run this as the right person".

        Raises:
            LakehouseAuthError: If no token is configured. There is no anonymous
                answer to this question, so unlike a query it cannot be served
                during the upgrade window.
        """
        if not self._is_initialized:
            self.initialize()

        if not self._pat:
            raise LakehouseAuthError(
                "No personal access token configured, so there is nobody to report. "
                "Generate one at https://cockpit.psr-inc.com and set it in the "
                "LAKEHOUSE_PAT environment variable."
            )
        return self._identity or {}

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
            LakehouseAuthError: If the token is missing, rejected or unentitled
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
            # `from None`: the chained HTTPError repeats the status, reason and
            # URL that _format_http_error already puts in the message, so all it
            # adds to a notebook traceback is two frames of requests internals
            # between the user and the sentence telling them what to do.
            raise self._http_error(e, url) from None
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Request to {url} failed: {e}") from e

    def get(self, endpoint: str, params: dict | None = None, _skip_init_check: bool = False) -> dict:
        """
        Make a GET request to the API.

        Args:
            endpoint: API endpoint path (e.g., "/query/whoami")
            params: Optional query parameters
            _skip_init_check: Internal. Set by initialize()'s own probe, which
                runs before _is_initialized is true and must not recurse into it.

        Returns:
            JSON response as dictionary

        Raises:
            LakehouseAuthError: If the token is missing, rejected or unentitled
            LakehouseError: If the request fails
        """
        if not self._is_initialized and not _skip_init_check:
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
            # `from None`: the chained HTTPError repeats the status, reason and
            # URL that _format_http_error already puts in the message, so all it
            # adds to a notebook traceback is two frames of requests internals
            # between the user and the sentence telling them what to do.
            raise self._http_error(e, url) from None
        except requests.exceptions.RequestException as e:
            raise LakehouseError(f"Request to {url} failed: {e}") from e

    def _http_error(self, error: requests.exceptions.HTTPError, url: str) -> LakehouseError:
        """Pick the exception class for an HTTP failure.

        401 and 403 become LakehouseAuthError, because what the caller has to
        do about them - get a token, or get a plan - has nothing to do with the
        query they wrote. The server's `detail` is appended as-is: it is a short
        stable sentence by contract, never the upstream identity provider's
        prose, so it is safe to put in a traceback.

        A 401 reads differently depending on whether a token was sent. During
        the upgrade window most of them will be from scripts that never had one,
        and telling those people to check a token they never set would send them
        looking for a bug instead of to the page that issues one.
        """
        status_code = error.response.status_code

        # Auth failures say one thing and say it once. The status, the URL and
        # the server's own wording all describe the same problem, so repeating
        # them buries the sentence that says what to do about it.
        if status_code == 401 and not self._pat:
            return LakehouseAuthError(
                "No personal access token was sent, and the PSR Lakehouse requires one. "
                "Generate a token at https://cockpit.psr-inc.com and set it in the "
                "LAKEHOUSE_PAT environment variable."
            )
        if status_code == 401:
            return LakehouseAuthError(
                "The personal access token was rejected. Check LAKEHOUSE_PAT, or generate "
                "a new token at https://cockpit.psr-inc.com."
            )
        if status_code == 403:
            # Here the server's wording is the whole point: it distinguishes
            # having no account from having no active plan, which send the
            # reader to different places.
            return LakehouseAuthError(f"{self._detail(error)} Check your account at https://cockpit.psr-inc.com.")
        return LakehouseError(self._format_http_error(error, url))

    @staticmethod
    def _detail(error: requests.exceptions.HTTPError) -> str:
        """The server's own sentence, without the status and URL around it."""
        try:
            body = error.response.json()
        except ValueError:
            return f"HTTP {error.response.status_code} {error.response.reason}."
        detail = body.get("detail", body) if isinstance(body, dict) else body
        return str(detail)

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
