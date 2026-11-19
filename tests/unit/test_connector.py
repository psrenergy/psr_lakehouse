import time

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
    def test_only_a_short_429_is_waited_out(self, monkeypatch):
        """The concurrency limit asks for seconds; a spent weekly quota asks for
        days, and must raise rather than hang."""
        from psr.lakehouse.connector import connector

        sleeps = []
        monkeypatch.setattr(time, "sleep", sleeps.append)
        url = "https://test-api.example.com/query/"
        responses.add(responses.POST, url, headers={"Retry-After": "2"}, status=429)
        responses.add(responses.POST, url, json={"data": []}, status=200)
        assert connector.post("/query/", {}) == {"data": []}
        assert sleeps == [2]

        responses.add(
            responses.POST, url, json={"detail": "Quota spent."}, headers={"Retry-After": "86400"}, status=429
        )
        with pytest.raises(LakehouseError, match="Quota spent"):
            connector.post("/query/", {})
        assert sleeps == [2]

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
        # Stripped: a token read from a file ends in a newline, which requests would echo whole.
        monkeypatch.setenv("LAKEHOUSE_PAT", "psr_from_env\n")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_startup("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert responses.calls[0].request.headers["Authorization"] == "Bearer psr_from_env"

    @responses.activate
    def test_missing_token_fails_at_initialize(self, monkeypatch):
        """The API refuses every query without a token, so say so on the line
        that set the client up, before any request goes out."""
        monkeypatch.delenv("LAKEHOUSE_PAT", raising=False)

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        with pytest.raises(LakehouseAuthError, match="LAKEHOUSE_PAT"):
            connector.initialize(base_url="https://api.example.com")

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
