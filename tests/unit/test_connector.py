import pytest
import requests
import responses

from psr.lakehouse.connector import Connector
from psr.lakehouse.exceptions import LakehouseAuthError, LakehouseError

# What GET /query/whoami actually serves: who you are and what you are on.
IDENTITY = {
    "full_name": "Someone",
    "email": "someone@psr-inc.com",
    "subscription": {"id": "a810e62f", "name": "PSR Staff", "description": "Internal access"},
}


def _mock_health_check(base_url):
    """Add a mock health check response for the given base URL."""
    responses.add(
        responses.GET,
        f"{base_url}/health-check",
        json=True,
        status=200,
    )


def _mock_whoami(base_url, json=IDENTITY, status=200):
    """Add a mock for the authenticated probe initialize() makes."""
    responses.add(
        responses.GET,
        f"{base_url}/query/whoami",
        json=json,
        status=status,
    )


def _mock_startup(base_url):
    """Both calls initialize() makes: reachability, then the token."""
    _mock_health_check(base_url)
    _mock_whoami(base_url)


class TestConnectorInitialization:
    @responses.activate
    def test_initialize_with_base_url(self):
        """Test initialization with explicit base URL."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://custom-api.example.com")
        connector.initialize(base_url="https://custom-api.example.com")

        assert connector._base_url == "https://custom-api.example.com"
        assert connector._is_initialized is True

    @responses.activate
    def test_initialize_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com/")

        assert connector._base_url == "https://api.example.com"

    @responses.activate
    def test_initialize_from_environment_variable(self, monkeypatch):
        """Test initialization from environment variable."""
        monkeypatch.setenv("LAKEHOUSE_API_URL", "https://env-api.example.com")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://env-api.example.com")
        connector.initialize()

        assert connector._base_url == "https://env-api.example.com"

    def test_initialize_raises_error_without_url(self, monkeypatch):
        """Test that initialization raises error when no URL is provided."""
        monkeypatch.delenv("LAKEHOUSE_API_URL", raising=False)

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        with pytest.raises(LakehouseError, match="API base URL not provided"):
            connector.initialize()

    @responses.activate
    def test_initialize_health_check_success(self):
        """Test that initialization succeeds when health check returns true."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert connector._is_initialized is True
        assert len(responses.calls) == 2
        assert "/health-check" in responses.calls[0].request.url
        assert "/query/whoami" in responses.calls[1].request.url

    @responses.activate
    def test_initialize_creates_session_with_retries(self):
        """Test that initialization creates a reusable session with retry configuration."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        retries = connector._session.get_adapter("https://api.example.com").max_retries
        assert retries.total == 3
        assert retries.backoff_factor == 1
        assert set(retries.status_forcelist) == {502, 503}
        assert set(retries.allowed_methods) == {"GET", "POST"}
        assert retries.respect_retry_after_header is False
        assert retries.raise_on_status is False

    @responses.activate
    def test_initialize_health_check_failure_error_status(self):
        """An error body is JSON too, and truthy: the status is what says the API is down."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        responses.add(
            responses.GET,
            "https://api.example.com/health-check",
            json={"detail": "Service unavailable."},
            status=503,
        )

        with pytest.raises(LakehouseError, match="Health check failed"):
            connector.initialize(base_url="https://api.example.com")

        assert connector._is_initialized is False

    @responses.activate
    def test_initialize_health_check_failure_non_truthy(self):
        """Test that initialization fails when health check returns non-truthy response."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        responses.add(
            responses.GET,
            "https://api.example.com/health-check",
            json=False,
            status=200,
        )

        with pytest.raises(LakehouseError, match="Health check failed"):
            connector.initialize(base_url="https://api.example.com")

        assert connector._is_initialized is False

    @responses.activate
    def test_initialize_health_check_connection_error(self):
        """Test that initialization fails when health check endpoint is unreachable."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        responses.add(
            responses.GET,
            "https://api.example.com/health-check",
            body=requests.exceptions.ConnectionError("Connection refused"),
        )

        with pytest.raises(LakehouseError, match="Health check failed"):
            connector.initialize(base_url="https://api.example.com")

        assert connector._is_initialized is False


class TestConnectorRequests:
    @responses.activate
    def test_post_request(self):
        """Test POST request."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        mock_response = {"data": [{"value": 1}], "pagination": {"has_next": False}}

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=mock_response,
            status=200,
        )

        result = connector.post("/query/", {"query_data": ["Model.column"]})

        assert result == mock_response
        assert len(responses.calls) == 3  # health check + whoami + POST

    @responses.activate
    def test_post_request_with_params(self):
        """Test POST request with query parameters."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        mock_response = {"data": [], "pagination": {"has_next": False}}

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json=mock_response,
            status=200,
        )

        result = connector.post("/query/", {"query_data": []}, params={"page": 1, "page_size": 100})

        assert result == mock_response
        assert "page=1" in responses.calls[2].request.url
        assert "page_size=100" in responses.calls[2].request.url

    @responses.activate
    def test_get_request(self):
        """Test GET request."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        mock_response = {"CCEESpotPrice": {"table_name": "ccee_spot_price", "columns": []}}

        responses.add(
            responses.GET,
            "https://test-api.example.com/query/schema",
            json=mock_response,
            status=200,
        )

        result = connector.get("/query/schema")

        assert result == mock_response
        assert len(responses.calls) == 3  # health check + whoami + GET

    @responses.activate
    def test_get_request_with_path_parameter(self):
        """Test GET request with path parameter."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        mock_response = {"model_name": "CCEESpotPrice", "table_name": "ccee_spot_price", "columns": []}

        responses.add(
            responses.GET,
            "https://test-api.example.com/query/schema/CCEESpotPrice",
            json=mock_response,
            status=200,
        )

        result = connector.get("/query/schema/CCEESpotPrice")

        assert result == mock_response

    @responses.activate
    def test_post_request_http_error(self):
        """Test POST request handling HTTP errors."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        responses.add(
            responses.POST,
            "https://test-api.example.com/query/",
            json={"detail": "Invalid model"},
            status=400,
        )

        with pytest.raises(LakehouseError, match="HTTP"):
            connector.post("/query/", {"query_data": ["InvalidModel.column"]})

    @responses.activate
    def test_get_request_http_error(self):
        """Test GET request handling HTTP errors."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://test-api.example.com")
        connector.initialize(base_url="https://test-api.example.com")

        responses.add(
            responses.GET,
            "https://test-api.example.com/query/schema/InvalidModel",
            json={"detail": "Model not found"},
            status=404,
        )

        with pytest.raises(LakehouseError, match="HTTP"):
            connector.get("/query/schema/InvalidModel")

    @pytest.mark.parametrize("method", ["POST", "GET"])
    @responses.activate
    def test_a_504_is_raised_once_with_the_server_detail(self, method):
        """A 504 is the server cancelling the query at its statement timeout:
        the same query fails the same way, and the detail says how to narrow it."""
        from psr.lakehouse.connector import connector

        responses.add(
            method,
            "https://test-api.example.com/query/",
            json={"detail": "The query took longer than 60 seconds and was cancelled."},
            status=504,
        )

        with pytest.raises(LakehouseError, match="HTTP 504 .* took longer than 60 seconds and was cancelled"):
            connector.post("/query/", {}) if method == "POST" else connector.get("/query/")

        assert len(responses.calls) == 1

    @pytest.mark.parametrize("status", [502, 503])
    @responses.activate
    def test_a_502_or_503_is_still_retried(self, status):
        from psr.lakehouse.connector import connector

        responses.add(responses.POST, "https://test-api.example.com/query/", status=status)
        responses.add(responses.POST, "https://test-api.example.com/query/", json={"data": []}, status=200)

        assert connector.post("/query/", {}) == {"data": []}
        assert len(responses.calls) == 2

    @pytest.mark.parametrize("status", [502, 503])
    @responses.activate
    def test_a_502_or_503_that_persists_carries_the_server_detail(self, status):
        from psr.lakehouse.connector import connector

        responses.add(
            responses.POST, "https://test-api.example.com/query/", json={"detail": "Warming up."}, status=status
        )

        with pytest.raises(LakehouseError, match=f"HTTP {status} .* Warming up"):
            connector.post("/query/", {})

        assert len(responses.calls) == 4  # the first attempt and three retries

    @responses.activate
    def test_auto_initialize_on_post(self, monkeypatch):
        """Test that connector auto-initializes on first POST request."""
        monkeypatch.setenv("LAKEHOUSE_API_URL", "https://auto-init-api.example.com")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://auto-init-api.example.com")

        mock_response = {"data": [], "pagination": {"has_next": False}}

        responses.add(
            responses.POST,
            "https://auto-init-api.example.com/query/",
            json=mock_response,
            status=200,
        )

        result = connector.post("/query/", {"query_data": []})

        assert connector._is_initialized is True
        assert result == mock_response

    @responses.activate
    def test_auto_initialize_on_get(self, monkeypatch):
        """Test that connector auto-initializes on first GET request."""
        monkeypatch.setenv("LAKEHOUSE_API_URL", "https://auto-init-api.example.com")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://auto-init-api.example.com")

        mock_response = {}

        responses.add(
            responses.GET,
            "https://auto-init-api.example.com/query/schema",
            json=mock_response,
            status=200,
        )

        result = connector.get("/query/schema")

        assert connector._is_initialized is True
        assert result == mock_response


class TestConnectorAuthentication:
    """The PAT the client now carries on every request.

    A token is not mandatory yet: the API is being gated, so a missing one
    warns and carries on until it is. What must hold today is that a token,
    when present, is attached to everything and resolved once at startup, and
    that it never turns up in an error message.
    """

    @responses.activate
    def test_token_is_sent_on_every_request(self, capsys):
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com", pat="psr_explicit")

        # Naming the holder is how a stale token gets caught before a day's work
        # is attributed to someone else.
        assert "Welcome, Someone!" in capsys.readouterr().err

        responses.add(
            responses.POST,
            "https://api.example.com/query/",
            json={"data": [], "pagination": {"has_next": False}},
            status=200,
        )
        connector.post("/query/", {"query_data": []})

        # The startup probes included, not just the query.
        for call in responses.calls:
            assert call.request.headers["Authorization"] == "Bearer psr_explicit"

    @responses.activate
    def test_token_falls_back_to_the_environment(self, monkeypatch):
        monkeypatch.setenv("LAKEHOUSE_PAT", "psr_from_env")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert responses.calls[0].request.headers["Authorization"] == "Bearer psr_from_env"

    @responses.activate
    def test_missing_token_warns_but_still_works(self, monkeypatch, capsys):
        """The upgrade window. Existing scripts must keep running, so a missing
        token warns today and errors only once the API is gated - and nothing
        half-authenticated goes out in the meantime."""
        monkeypatch.delenv("LAKEHOUSE_PAT", raising=False)

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert "cockpit.psr-inc.com" in capsys.readouterr().err
        assert connector._is_initialized is True
        assert "Authorization" not in connector._session.headers
        # Health check only: no whoami probe that could only 401.
        assert len(responses.calls) == 1

    @responses.activate
    def test_whitespace_around_the_token_is_stripped(self, monkeypatch):
        """A trailing newline from `$(cat token.txt)` is the usual one."""
        monkeypatch.setenv("LAKEHOUSE_PAT", " psr_from_env\n")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert responses.calls[0].request.headers["Authorization"] == "Bearer psr_from_env"

    @pytest.mark.parametrize("pat", ["psr_secret value", "psr_secret\tvalue"])
    @responses.activate
    def test_a_malformed_token_fails_at_initialize_without_naming_itself(self, monkeypatch, pat):
        """Left to requests, its complaint about the header quotes the token in
        full. And a failed initialize() changes nothing."""
        from psr.lakehouse.connector import connector

        monkeypatch.setenv("LAKEHOUSE_PAT", pat)
        monkeypatch.setattr(connector, "_pat", "psr_test_token")

        with pytest.raises(LakehouseAuthError, match="whitespace") as error:
            connector.initialize(base_url="https://api.example.com")

        assert "psr_secret" not in str(error.value)
        assert connector._pat == "psr_test_token"
        assert connector._session.headers["Authorization"] == "Bearer psr_test_token"
        assert len(responses.calls) == 0

    @responses.activate
    def test_a_rejected_token_fails_at_initialize_without_naming_itself(self):
        """The point of probing at startup: a 401 on the line that set the token
        up, not one an hour into a job. And the message lands in a traceback,
        which lands in a notebook, which gets shared."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://api.example.com")
        _mock_whoami("https://api.example.com", json={"detail": "Invalid token."}, status=401)

        with pytest.raises(LakehouseAuthError, match="rejected") as error:
            connector.initialize(base_url="https://api.example.com", pat="psr_super_secret_value")

        assert "psr_super_secret_value" not in str(error.value)

    @responses.activate
    def test_no_active_plan_reads_differently_from_a_bad_token(self):
        """403 is not 401: the token is fine, the subscription is not, and
        telling someone to check their token sends them to the wrong page."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://api.example.com")
        _mock_whoami("https://api.example.com", json={"detail": "No active plan."}, status=403)

        # The server's own sentence survives: it is what distinguishes a lapsed
        # plan from having no account at all.
        with pytest.raises(LakehouseAuthError, match="No active plan"):
            connector.initialize(base_url="https://api.example.com", pat="psr_valid")

    @responses.activate
    def test_a_401_without_a_token_does_not_blame_the_token(self, monkeypatch):
        """The common case once the API is gated: a script that never had one.
        Telling those people to check LAKEHOUSE_PAT sends them hunting for a bug
        instead of to the page that issues tokens."""
        monkeypatch.delenv("LAKEHOUSE_PAT", raising=False)

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        responses.add(
            responses.POST,
            "https://api.example.com/query/",
            json={"detail": "A PSR personal access token is required"},
            status=401,
        )

        with pytest.raises(LakehouseAuthError, match="No personal access token was sent") as error:
            connector.post("/query/", {"query_data": []})

        assert "rejected" not in str(error.value)


class TestConnectorUsage:
    @responses.activate
    def test_usage_refetches_and_prints_limits(self, capsys, monkeypatch):
        """Rows used move with every query, so usage() asks again rather than
        reporting what initialize() saw."""
        from psr.lakehouse.connector import connector

        monkeypatch.setattr(connector, "_pat", "psr_test_token")
        connector._identity = {**IDENTITY, "limits": {"weekly_row_quota": 1000, "weekly_rows_used": 0}}
        _mock_whoami(
            "https://test-api.example.com",
            json={
                **IDENTITY,
                "tables": ["CCEESpotPrice", "CCEEAgentProfile", "ONSLoadCurve"],
                "limits": {"weekly_row_quota": 1000, "weekly_rows_used": 250, "max_concurrent_queries": 4},
            },
        )

        connector.usage()

        out = capsys.readouterr().out
        assert "Someone <someone@psr-inc.com>" in out
        assert "PSR Staff (Internal access)" in out
        assert "3 available from 2 sources" in out
        assert "CCEE 2, ONS 1" in out
        assert "CCEESpotPrice" not in out
        assert "250 / 1,000 (25%)" in out
        assert "750 left this week" in out
        assert "oncurrent" not in out
        assert connector._identity["limits"]["weekly_rows_used"] == 250

    def test_format_usage_without_plan_or_quota(self):
        from psr.lakehouse.connector import _format_usage

        out = _format_usage(
            {
                "full_name": "Someone",
                "email": "someone@psr-inc.com",
                "subscription": None,
                "limits": {"weekly_row_quota": None, "weekly_rows_used": 12},
            },
            "https://api.example.com",
        )

        assert "Plan      none" in out
        assert "12 used (no quota)" in out

    def test_group_by_source(self):
        from psr.lakehouse.connector import _group_by_source

        assert _group_by_source(
            [
                "ONSEnergyBalanceSubsystem",
                "ONSLoadCurve",
                "CLCENPowerPlant",
                "CLCenSpotPriceNodeQuarterHourly",
                "DcideCompiledCurve",
            ]
        ) == {"CLCEN": 2, "Dcide": 1, "ONS": 2}

    def test_usage_without_a_token_raises(self, monkeypatch):
        from psr.lakehouse.connector import connector

        monkeypatch.setattr(connector, "_pat", None)

        with pytest.raises(LakehouseAuthError):
            connector.usage()


class TestScopedToken:
    """One process serving several people, each request on its own token.

    What must hold: a scoped token overrides the global one on every request
    in its block and nowhere else, concurrent scopes never see each other's
    token, and strict mode fails closed instead of falling back.
    """

    URL = "https://test-api.example.com"

    @pytest.fixture(autouse=True)
    def global_pat(self, monkeypatch):
        from psr.lakehouse.connector import connector

        monkeypatch.setattr(connector, "_pat", "psr_test_token")

    def _strict(self, monkeypatch):
        """Initialize as a multi-tenant server would: no process-wide token."""
        from psr.lakehouse.connector import connector

        monkeypatch.setenv("LAKEHOUSE_PAT", "psr_from_env")
        _mock_health_check(self.URL)
        connector.initialize(base_url=self.URL, require_scoped_token=True)
        responses.calls.reset()
        return connector

    @responses.activate
    def test_without_a_scope_the_session_header_goes_unchanged(self):
        from psr.lakehouse.connector import connector

        responses.add(responses.GET, f"{self.URL}/query/schema", json={})
        responses.add(responses.POST, f"{self.URL}/query/", json={})

        connector.get("/query/schema")
        connector.post("/query/", {})

        for call in responses.calls:
            assert call.request.headers["Authorization"] == "Bearer psr_test_token"

    @responses.activate
    def test_a_scope_overrides_the_global_token_on_get_and_post(self):
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        responses.add(responses.GET, f"{self.URL}/query/schema", json={})
        responses.add(responses.POST, f"{self.URL}/query/", json={})

        with scoped_token("psr_alice"):
            connector.get("/query/schema")
            connector.post("/query/", {})

        assert [c.request.headers["Authorization"] for c in responses.calls] == ["Bearer psr_alice"] * 2

    @responses.activate
    def test_the_scope_is_reset_on_exit_even_when_the_body_raises(self):
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        responses.add(responses.GET, f"{self.URL}/query/schema", json={})

        with pytest.raises(RuntimeError), scoped_token("psr_alice"):
            raise RuntimeError
        connector.get("/query/schema")

        assert responses.calls[0].request.headers["Authorization"] == "Bearer psr_test_token"

    @responses.activate
    def test_nested_scopes_restore_the_outer_token(self):
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        responses.add(responses.GET, f"{self.URL}/query/schema", json={})

        with scoped_token("psr_outer"):
            with scoped_token("psr_inner"):
                connector.get("/query/schema")
            connector.get("/query/schema")
        connector.get("/query/schema")

        assert [c.request.headers["Authorization"] for c in responses.calls] == [
            "Bearer psr_inner",
            "Bearer psr_outer",
            "Bearer psr_test_token",
        ]

    @responses.activate
    def test_concurrent_scopes_each_send_their_own_token(self):
        """Both threads enter their scope before either builds its request, and
        both requests are held in flight together, so a token kept on shared
        state would be seen by the other thread."""
        import contextvars
        import threading

        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        both_scoped = threading.Barrier(2, timeout=5)
        both_in_flight = threading.Barrier(2, timeout=5)
        seen = {}

        def answer(request):
            both_in_flight.wait()
            seen[request.url.rsplit("/", 1)[1]] = request.headers["Authorization"]
            return 200, {}, "{}"

        responses.add_callback(responses.GET, f"{self.URL}/query/psr_alice", callback=answer)
        responses.add_callback(responses.GET, f"{self.URL}/query/psr_bob", callback=answer)

        def work(pat):
            with scoped_token(pat):
                both_scoped.wait()
                connector.get(f"/query/{pat}")

        threads = [
            threading.Thread(target=contextvars.copy_context().run, args=(work, pat))
            for pat in ("psr_alice", "psr_bob")
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert seen == {"psr_alice": "Bearer psr_alice", "psr_bob": "Bearer psr_bob"}

    @responses.activate
    def test_a_401_under_a_scope_says_rejected_even_with_no_global_token(self, monkeypatch):
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        monkeypatch.setattr(connector, "_pat", None)
        del connector._session.headers["Authorization"]
        responses.add(responses.POST, f"{self.URL}/query/", json={"detail": "Invalid token."}, status=401)

        with pytest.raises(LakehouseAuthError, match="rejected") as error, scoped_token("psr_secret_value"):
            connector.post("/query/", {})

        assert "No personal access token was sent" not in str(error.value)
        # The token came from whoever the process serves, not its environment.
        assert "LAKEHOUSE_PAT" not in str(error.value)
        assert "psr_secret_value" not in str(error.value)

    @responses.activate
    def test_whoami_and_usage_under_a_scope_ask_for_the_scoped_token(self, capsys):
        """Never the identity held for the global token, and never stored over it."""
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        connector._identity = IDENTITY
        alice = {**IDENTITY, "full_name": "Alice", "email": "alice@example.com"}
        _mock_whoami(self.URL, json=alice)

        with scoped_token("psr_alice"):
            assert connector.whoami() == alice
            connector.usage()

        assert "Alice <alice@example.com>" in capsys.readouterr().out
        assert [c.request.headers["Authorization"] for c in responses.calls] == ["Bearer psr_alice"] * 2
        assert connector._identity is IDENTITY
        assert connector.whoami() is IDENTITY

    @responses.activate
    def test_initialize_inside_a_scope_resolves_the_global_token(self, monkeypatch):
        """The automatic initialize() can run inside the first scope. Its probe
        must not hold that person as the process's identity."""
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        monkeypatch.setattr(connector, "_is_initialized", False)
        _mock_startup(self.URL)
        responses.add(responses.GET, f"{self.URL}/query/schema", json={})

        with scoped_token("psr_alice"):
            connector.get("/query/schema")

        assert responses.calls[1].request.headers["Authorization"] == "Bearer psr_test_token"
        assert responses.calls[2].request.headers["Authorization"] == "Bearer psr_alice"
        assert connector._identity == IDENTITY

    @pytest.mark.parametrize("pat", [None, "", " ", "psr_a b", "psr_a\r\nX-Evil: 1", 42])
    def test_a_missing_or_malformed_scoped_token_is_refused_without_quoting_it(self, pat):
        """A None must not fall back to the global token, and requests' own
        complaint about a bad header quotes the header."""
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import _scoped_pat

        with pytest.raises(LakehouseAuthError) as error, scoped_token(pat):
            pass

        assert "psr_a" not in str(error.value)
        assert _scoped_pat.get() is None

    @responses.activate
    def test_strict_mode_ignores_the_environment_and_refuses_unscoped_requests(self, monkeypatch, capsys):
        from psr.lakehouse import scoped_token

        connector = self._strict(monkeypatch)

        assert connector._pat is None
        assert "Authorization" not in connector._session.headers
        # Its advice, set LAKEHOUSE_PAT, is the wrong one for a server.
        assert "cockpit" not in capsys.readouterr().err

        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.post("/query/", {})
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.get("/query/schema")
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.whoami()
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.usage()
        assert len(responses.calls) == 0

        responses.add(responses.POST, f"{self.URL}/query/", json={})
        with scoped_token("psr_alice"):
            connector.post("/query/", {})
        assert responses.calls[0].request.headers["Authorization"] == "Bearer psr_alice"

    @responses.activate
    def test_strict_mode_fails_closed_when_work_loses_its_scope(self, monkeypatch):
        """The documented caveat: a ThreadPoolExecutor does not carry the scope."""
        from concurrent.futures import ThreadPoolExecutor

        from psr.lakehouse import scoped_token

        connector = self._strict(monkeypatch)

        with scoped_token("psr_alice"), ThreadPoolExecutor(1) as pool:
            future = pool.submit(connector.get, "/query/schema")
            with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
                future.result()
        assert len(responses.calls) == 0

    @responses.activate
    def test_strict_mode_survives_reinitializing_and_refuses_a_global_pat(self, monkeypatch):
        connector = self._strict(monkeypatch)

        _mock_health_check(self.URL)
        connector.initialize(base_url=self.URL)
        assert connector._pat is None
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.get("/query/schema")

        with pytest.raises(LakehouseError, match="require_scoped_token") as error:
            connector.initialize(base_url=self.URL, pat="psr_super_secret_value")
        assert "psr_super_secret_value" not in str(error.value)
        assert connector._pat is None

    def test_a_failed_strict_initialize_leaves_no_global_token_behind(self, monkeypatch):
        from psr.lakehouse.connector import connector

        monkeypatch.delenv("LAKEHOUSE_API_URL")
        with pytest.raises(LakehouseError, match="API base URL"):
            connector.initialize(require_scoped_token=True)

        assert connector._pat is None
        assert "Authorization" not in connector._session.headers
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.get("/query/schema")

    @responses.activate
    def test_a_malformed_pat_does_not_turn_strict_mode_off(self, monkeypatch):
        """The token is checked before the flag changes, so a failed call
        leaves the process failing closed, not sending unscoped requests."""
        connector = self._strict(monkeypatch)

        with pytest.raises(LakehouseAuthError, match="whitespace"):
            connector.initialize(base_url=self.URL, pat="psr_a b", require_scoped_token=False)

        assert connector._require_scoped_token is True
        with pytest.raises(LakehouseAuthError, match="outside scoped_token"):
            connector.get("/query/schema")

    @responses.activate
    def test_the_session_keeps_no_cookies(self):
        """The session is shared across scopes, so a cookie from one person's
        response must not ride on the next person's request."""
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        responses.add(responses.GET, f"{self.URL}/query/a", json={}, headers={"Set-Cookie": "sid=alice; Path=/"})
        responses.add(responses.GET, f"{self.URL}/query/b", json={})

        with scoped_token("psr_alice"):
            connector.get("/query/a")
        with scoped_token("psr_bob"):
            connector.get("/query/b")

        assert "Cookie" not in responses.calls[1].request.headers

    @responses.activate
    def test_a_netrc_entry_does_not_replace_the_scoped_token(self, monkeypatch, tmp_path):
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        netrc = tmp_path / "netrc"
        netrc.write_text("machine test-api.example.com login ops password ops_secret\n")
        monkeypatch.setenv("NETRC", str(netrc))
        connector._session = connector._create_session()
        responses.add(responses.GET, f"{self.URL}/query/redirect", status=307, headers={"Location": "/query/schema"})
        responses.add(responses.GET, f"{self.URL}/query/schema", json={})

        with scoped_token("psr_alice"):
            connector.get("/query/redirect")

        # The redirect too, where requests looks up ~/.netrc again.
        assert [c.request.headers["Authorization"] for c in responses.calls] == ["Bearer psr_alice"] * 2

    @responses.activate
    def test_a_context_copied_inside_a_block_loses_the_token_when_it_exits(self, monkeypatch):
        """What a worker thread or a suspended generator holds. In strict mode,
        work left on it after the block raises instead of sending the token."""
        import contextvars

        from psr.lakehouse import scoped_token

        connector = self._strict(monkeypatch)

        with scoped_token("psr_alice"):
            copied = contextvars.copy_context()

        with pytest.raises(LakehouseAuthError, match="block exited"):
            copied.run(connector.get, "/query/schema")
        assert len(responses.calls) == 0

    @responses.activate
    def test_a_task_that_outlives_its_block_does_not_fall_back_to_the_global_token(self):
        """Without strict mode too: the task was started for Alice, so sending
        the process's own token would run her work as someone else."""
        import asyncio

        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import connector

        async def main():
            gate = asyncio.Event()

            async def background():
                await gate.wait()
                connector.get("/query/schema")

            with scoped_token("psr_alice"):
                task = asyncio.create_task(background())
            gate.set()
            await task

        with pytest.raises(LakehouseAuthError, match="block exited"):
            asyncio.run(main())
        assert len(responses.calls) == 0

    def test_a_scope_held_across_a_yield_is_not_handed_on(self):
        """Two generators interleaved in one context. Alice's block exits while
        Bob's is in effect; when Bob's exits, nothing of Alice's comes back."""
        from psr.lakehouse import scoped_token
        from psr.lakehouse.connector import _scoped

        def stream(pat):
            with scoped_token(pat):
                yield

        alice, bob = stream("psr_alice"), stream("psr_bob")
        next(alice)
        next(bob)
        with pytest.raises(LakehouseAuthError, match="out of order"):
            next(alice)
        assert _scoped() == "psr_bob"
        next(bob, None)

        # What comes back is Alice's emptied cell, which refuses unscoped work.
        with pytest.raises(LakehouseAuthError, match="block exited"):
            _scoped()
