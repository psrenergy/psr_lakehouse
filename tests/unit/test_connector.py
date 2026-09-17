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
        assert set(retries.status_forcelist) == {502, 503, 504}
        assert set(retries.allowed_methods) == {"GET", "POST"}

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
