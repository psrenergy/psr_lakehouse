import contextvars
import os
import re
import sys
import textwrap
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from importlib import metadata

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from psr.lakehouse.exceptions import LakehouseAuthError, LakehouseError

# The token of whoever the current thread or task is working for, set by
# scoped_token(). A context variable rather than an attribute on the connector,
# which every thread shares: each context sees only the token it set. It holds
# a one-item list rather than the token, so that closing the block empties it
# for every context that copied it: a worker thread, a suspended generator.
_scoped_pat: contextvars.ContextVar[list[str | None] | None] = contextvars.ContextVar(
    "lakehouse_scoped_pat", default=None
)


def _scoped() -> str | None:
    """The scoped token in effect here, if its block is still open."""
    cell = _scoped_pat.get()
    return cell[0] if cell else None


_NO_TOKEN = (
    "No personal access token configured, so there is nobody to report. "
    "Generate one at https://cockpit.psr-inc.com and set it in the "
    "LAKEHOUSE_PAT environment variable."
)
_OUTSIDE_SCOPE = "This request was made outside scoped_token() while require_scoped_token is on, so it was not sent."


def _well_formed(pat: object) -> bool:
    """Visible ASCII only. Checked before a token goes in a header, because
    requests rejects a malformed header with a message that quotes it."""
    return isinstance(pat, str) and re.fullmatch(r"[!-~]+", pat) is not None


class Connector:
    _instance = None

    _is_initialized: bool = False
    _base_url: str
    _session: requests.Session
    _identity: dict | None = None
    _pat: str | None = None
    _require_scoped_token: bool = False
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
                # deliberately absent: a bad token must fail fast. So is 504: it
                # is the server cancelling the query at its statement timeout, so
                # a retry only runs the same query again to fail the same way.
                status_forcelist=[502, 503],
                allowed_methods=["GET", "POST"],
                # Without this, urllib3 also retries any 429 that carries a
                # Retry-After, and sleeps for it: a spent weekly row quota
                # answers with days, so the call hangs instead of raising.
                respect_retry_after_header=False,
                # Once the retries run out, hand back the last response rather
                # than raise "too many 503 error responses": raise_for_status()
                # then reports its status and the server's detail.
                raise_on_status=False,
            )
        )
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def initialize(
        self,
        base_url: str | None = None,
        pat: str | None = None,
        require_scoped_token: bool | None = None,
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
            require_scoped_token: For a process serving several people. When
                True there is no process-wide token: LAKEHOUSE_PAT is
                ignored, passing `pat` raises, and any request made outside
                scoped_token() raises LakehouseAuthError before it is sent. It
                stays on for later initialize() calls, the automatic one
                included, until one passes False.

        Raises:
            LakehouseAuthError: If the token is rejected, or if its owner holds
                no active Lakehouse plan.
            LakehouseError: If the API URL is missing, the API is unreachable,
                or `pat` is given while require_scoped_token is on.

        Note:
            A token is not yet mandatory. Without one this warns and carries on,
            so existing scripts keep running until the API starts requiring it.
        """
        # First, before anything can raise, so that a failed initialize() in
        # strict mode leaves no global token behind.
        if require_scoped_token is not None:
            self._require_scoped_token = require_scoped_token
        if self._require_scoped_token:
            self._pat = None
            self._identity = None
            if pat:
                raise LakehouseError("pat cannot be given while require_scoped_token is on; use scoped_token().")

        # Get base URL from parameter or environment variable
        self._base_url = base_url or os.getenv("LAKEHOUSE_API_URL")
        if not self._base_url:
            raise LakehouseError(
                "API base URL not provided. Set LAKEHOUSE_API_URL environment variable or pass base_url parameter."
            )
        self._base_url = self._base_url.rstrip("/")

        self._pat = None if self._require_scoped_token else pat or os.getenv("LAKEHOUSE_PAT")
        self._identity = None

        self._session = self._create_session()
        if self._pat:
            # Set on the session rather than per call, so no request can be
            # added later that forgets to carry it.
            self._session.headers["Authorization"] = f"Bearer {self._pat}"
        elif not self._require_scoped_token:
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
            installed = metadata.version("psr-lakehouse")
        except metadata.PackageNotFoundError:
            # Running from a source tree that was never installed.
            installed = "unknown"

        try:
            # The version rides on this one request rather than on every one.
            # It is the only way the API can tell a user who has not set a token
            # from one whose client is too old to send one - the advice differs
            # entirely - and that is a fact about the session, not about each
            # query, so stating it once is enough.
            response = self._session.get(
                f"{self._base_url}/health-check",
                headers={"X-PSR-Lakehouse-Version": installed},
                timeout=10,
            )
            # An error answer is JSON too, and truthy.
            response.raise_for_status()
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
            # With the scope cleared, so that an initialize() triggered inside
            # scoped_token() resolves the global token, not the scoped one.
            probe = contextvars.copy_context()
            probe.run(_scoped_pat.set, None)
            self._identity = probe.run(self.get, "/query/whoami", _skip_init_check=True)
            # Greeting the person by name is the shortest way to answer the two
            # questions a token raises - is it working, and whose is it. Reading
            # the wrong name here is how someone catches a stale LAKEHOUSE_PAT
            # before a day's analysis is attributed to a colleague.
            name = self._identity.get("full_name") or self._identity.get("email") or "back"
            print(f"Welcome, {name}!", file=sys.stderr)

        self._is_initialized = True

    @contextmanager
    def scoped_token(self, pat: str) -> Iterator[None]:
        """Send `pat` instead of the global token on every request in this block.

        For a process serving several people, each with their own token::

            with scoped_token(pat):
                client.fetch_dataframe(...)

        The token is held in a context variable, so concurrent threads and
        tasks each see only their own. Blocks nest; the inner one wins until
        it exits. When a block exits, exception or not, its token is gone from
        every context, copies included.

        Context variables follow asyncio tasks and anyio's `to_thread`, which
        copy the context. A `threading.Thread` or a
        `concurrent.futures.ThreadPoolExecutor` does not: work handed to one
        runs without the scoped token and falls back to the global one, or to
        none. Start such work with `contextvars.copy_context().run`, and
        initialize with `require_scoped_token=True` so that a lost scope raises
        instead of falling back. On Python 3.14 with thread context
        inheritance on (the free-threaded default), a thread instead copies the
        context it was started from, so a pool started inside a block runs
        everyone's unscoped work with that block's token until it exits.
        Start pools outside any block.

        Never hold a block open across a `yield`, in a generator or an async
        generator: while the generator is suspended its caller's context sees
        the token. Open the block around each request instead. A block that
        exits out of order raises.

        Raises:
            LakehouseAuthError: If `pat` is empty, not a string, or holds
                whitespace or control characters, or if the block exits out
                of order.
        """
        # A None, too, which would otherwise fall back to the global token.
        if not _well_formed(pat):
            raise LakehouseAuthError("The scoped personal access token is empty or malformed.")
        cell = [pat]
        reset_to = _scoped_pat.set(cell)
        try:
            yield
        finally:
            # Emptied first, so no context that copied the cell keeps the token.
            cell[0] = None
            # Another block's cell here means this one was held across a yield.
            # That block is still open, so its token stays.
            if _scoped_pat.get() is not cell:
                raise LakehouseAuthError(
                    "A scoped_token() block exited out of order, which happens when one is held open across a yield."
                )
            # Entered in another context: leaving the emptied cell in place is safe.
            with suppress(ValueError):
                _scoped_pat.reset(reset_to)

    def _token(self) -> str | None:
        """The token in effect here: the scoped one, else the global one."""
        scoped = _scoped()
        if scoped is not None:
            return scoped
        return None if self._require_scoped_token else self._pat

    def _auth_headers(self) -> dict | None:
        """The per-call Authorization a scoped token rides on.

        requests merges it over the session's header, so it wins. Outside a
        scope there is none and the session's header goes as before, unless
        scoped tokens are required, when the request must not go at all.
        """
        scoped = _scoped()
        if scoped is not None:
            return {"Authorization": f"Bearer {scoped}"}
        if self._require_scoped_token:
            raise LakehouseAuthError(_OUTSIDE_SCOPE)
        return None

    def whoami(self) -> dict:
        """Return who the token in effect belongs to, and the plan it carries.

        For the global token this is resolved once at initialize() and held,
        so it is free to call. Inside scoped_token() it asks the API, for that
        token. It is the answer to "am I about to run this as the right person".

        Raises:
            LakehouseAuthError: If no token is configured. There is no anonymous
                answer to this question, so unlike a query it cannot be served
                during the upgrade window. With require_scoped_token, if called
                outside scoped_token().
        """
        if not self._is_initialized:
            self.initialize()

        if not self._token():
            raise LakehouseAuthError(_OUTSIDE_SCOPE if self._require_scoped_token else _NO_TOKEN)
        if _scoped() is not None:
            return self.get("/query/whoami")
        return self._identity or {}

    def usage(self) -> None:
        """Print the account, its plan and how much of the plan's limits are used.

        Unlike whoami(), this asks the API again: rows used move with every
        query, so the figure held since initialize() would be stale by the time
        anyone wants to know how much quota is left.

        Raises:
            LakehouseAuthError: If no token is configured, or, with
                require_scoped_token, if called outside scoped_token().
        """
        if not self._is_initialized:
            self.initialize()

        if not self._token():
            raise LakehouseAuthError(_OUTSIDE_SCOPE if self._require_scoped_token else _NO_TOKEN)
        identity = self.get("/query/whoami")
        # What is held is the global token's identity; a scoped one is not kept.
        if _scoped() is None:
            self._identity = identity
        print(_format_usage(identity, self._base_url))

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
                headers=self._auth_headers(),
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
                headers=self._auth_headers(),
                # Longer than the server's 60 s statement timeout, so its 504
                # arrives before the read timeout, which is retried.
                timeout=90,
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
        if status_code == 401 and not self._token():
            return LakehouseAuthError(
                "No personal access token was sent, and the PSR Lakehouse requires one. "
                "Generate a token at https://cockpit.psr-inc.com and set it in the "
                "LAKEHOUSE_PAT environment variable."
            )
        if status_code == 401 and _scoped() is not None:
            # Not "check LAKEHOUSE_PAT": the token came from whoever this
            # process is serving, not from its environment.
            return LakehouseAuthError(
                "The personal access token was rejected. Generate a new token at https://cockpit.psr-inc.com."
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


def _format_usage(identity: dict, base_url: str) -> str:
    """Render GET /query/whoami as the block usage() prints."""
    name = identity.get("full_name") or "Unknown"
    subscription = identity.get("subscription")
    if subscription:
        plan = subscription.get("name") or "Unnamed plan"
        if subscription.get("description"):
            plan = f"{plan} ({subscription['description']})"
    else:
        plan = "none"

    lines = [
        "PSR Lakehouse",
        f"  Account   {name} <{identity.get('email')}>",
        f"  Plan      {plan}",
        f"  API       {base_url}",
    ]

    tables = identity.get("tables")
    if tables is not None:
        sources = _group_by_source(tables)
        lines.append(f"  Tables    {len(tables)} available from {len(sources)} sources")
        summary = ", ".join(f"{source} {count}" for source, count in sources.items())
        lines.extend(textwrap.wrap(summary, width=78, initial_indent=" " * 12, subsequent_indent=" " * 12))
        lines.append("            client.list_tables() lists them all")

    limits = identity.get("limits") or {}
    if limits:
        lines.append("")
        lines.append("Limits")
        quota = limits.get("weekly_row_quota")
        used = limits.get("weekly_rows_used") or 0
        if quota is None:
            lines.append(f"  Weekly rows  {used:,} used (no quota)")
        else:
            share = min(used / quota, 1.0) if quota else 1.0
            lines.append(f"  Weekly rows  {_bar(share)} {used:,} / {quota:,} ({share:.0%})")
            lines.append(f"               {max(quota - used, 0):,} left this week")

    return "\n".join(lines)


def _group_by_source(tables: list[str]) -> dict[str, int]:
    """Count tables per data source, the acronym their names start with.

    A plan can reach over a hundred tables, too many to list here. The source
    is the leading capitals before the first word ("ONS" in ONSLoadCurve).
    Names that spell the source differently (CLCenSpot... beside CLCEN...)
    join the longest source they start with, ignoring case.
    """
    prefixes = set()
    for table in tables:
        match = re.match(r"[A-Z]+(?=[A-Z][a-z])", table) or re.match(r"[A-Z][a-z]+", table)
        prefixes.add(match.group(0) if match else table)

    counts: dict[str, int] = {}
    for table in tables:
        source = max((p for p in prefixes if table.lower().startswith(p.lower())), key=len, default=table)
        counts[source] = counts.get(source, 0) + 1
    return dict(sorted(counts.items()))


def _bar(share: float, width: int = 20) -> str:
    # Block characters where the terminal can show them; a Windows console
    # redirected to a cp1252 file cannot, and would raise on print.
    full, empty = "█", "░"
    try:
        (full + empty).encode(sys.stdout.encoding or "ascii")
    except (UnicodeEncodeError, LookupError):
        full, empty = "#", "-"
    filled = round(share * width)
    return f"[{full * filled}{empty * (width - filled)}]"


connector = Connector()
