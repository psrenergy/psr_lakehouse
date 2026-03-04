import pytest
import requests
import responses

from psr.lakehouse.connector import Connector
from psr.lakehouse.exceptions import LakehouseError


def _mock_health_check(base_url):
    """Add a mock health check response for the given base URL."""
    responses.add(
        responses.GET,
        f"{base_url}/health-check",
        json=True,
        status=200,
    )


class TestConnectorInitialization:
    @responses.activate
    def test_initialize_with_base_url(self):
        """Test initialization with explicit base URL."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://custom-api.example.com")
        connector.initialize(base_url="https://custom-api.example.com")

        assert connector._base_url == "https://custom-api.example.com"
        assert connector._is_initialized is True

    @responses.activate
    def test_initialize_strips_trailing_slash(self):
        """Test that trailing slash is stripped from base URL."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://api.example.com")
        connector.initialize(base_url="https://api.example.com/")

        assert connector._base_url == "https://api.example.com"

    @responses.activate
    def test_initialize_from_environment_variable(self, monkeypatch):
        """Test initialization from environment variable."""
        monkeypatch.setenv("LAKEHOUSE_API_URL", "https://env-api.example.com")

        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://env-api.example.com")
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

        _mock_health_check("https://api.example.com")
        connector.initialize(base_url="https://api.example.com")

        assert connector._is_initialized is True
        assert len(responses.calls) == 1
        assert "/health-check" in responses.calls[0].request.url

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

        _mock_health_check("https://test-api.example.com")
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
        assert len(responses.calls) == 2  # health check + POST

    @responses.activate
    def test_post_request_with_params(self):
        """Test POST request with query parameters."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://test-api.example.com")
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
        assert "page=1" in responses.calls[1].request.url
        assert "page_size=100" in responses.calls[1].request.url

    @responses.activate
    def test_get_request(self):
        """Test GET request."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://test-api.example.com")
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
        assert len(responses.calls) == 2  # health check + GET

    @responses.activate
    def test_get_request_with_path_parameter(self):
        """Test GET request with path parameter."""
        connector = Connector.__new__(Connector)
        connector._is_initialized = False

        _mock_health_check("https://test-api.example.com")
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

        _mock_health_check("https://test-api.example.com")
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

        _mock_health_check("https://test-api.example.com")
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

        _mock_health_check("https://auto-init-api.example.com")

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

        _mock_health_check("https://auto-init-api.example.com")

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
