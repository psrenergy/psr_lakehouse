import json
import time

import pytest
import requests

from psr.lakehouse import auth
from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseAuthError

BASE_URL = "https://test-api.example.com"
IDP = "https://accounts.example.com"
AUTHORIZE_URL = f"{IDP}/oauth2/authorize?client_id=abc&redirect_uri={BASE_URL}/oauth2/idpresponse&state=xyz"

# What the browser is left showing: a 401 whose URL still carries the unspent code.
CALLBACK_URL = f"{BASE_URL}/oauth2/idpresponse?code=auth-code&state=xyz"


@pytest.fixture(autouse=True)
def session_file(tmp_path, monkeypatch):
    """Keep every test off the real ~/.psr-lakehouse/session.json."""
    path = tmp_path / "session.json"
    monkeypatch.setenv("LAKEHOUSE_SESSION_FILE", str(path))
    monkeypatch.delenv("LAKEHOUSE_AUTO_LOGIN", raising=False)
    return path


@pytest.fixture(autouse=True)
def dont_open_a_browser(monkeypatch):
    opened = []
    monkeypatch.setattr(auth, "_open_browser", opened.append)
    return opened


def bounce(mock_api, path=f"{BASE_URL}/openapi.json"):
    """The load balancer answering an unauthenticated request."""
    mock_api.add(mock_api.GET, path, status=302, headers={"Location": AUTHORIZE_URL})


def callback_succeeds(mock_api, expires=None):
    """The replayed callback: the load balancer spends the code and hands over its cookie."""
    cookie = "AWSELBAuthSessionCookie-0=session-value; Path=/"
    if expires:
        cookie += f"; Expires={time.strftime('%a, %d-%b-%Y %H:%M:%S GMT', time.gmtime(expires))}"
    mock_api.add(
        mock_api.GET,
        f"{BASE_URL}/oauth2/idpresponse",
        status=200,
        json={"openapi": "3.1.0"},
        headers={"Set-Cookie": cookie},
    )


def authenticated(mock_api, path=f"{BASE_URL}/openapi.json"):
    mock_api.add(mock_api.GET, path, status=200, json={"openapi": "3.1.0"})


def log_in(mock_api, monkeypatch, expires=None):
    """Complete a login, so a test can start from a cached session."""
    bounce(mock_api)
    callback_succeeds(mock_api, expires=expires)
    authenticated(mock_api)
    monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)
    auth.login(BASE_URL)


class TestLogin:
    def test_replays_the_pasted_callback_to_collect_the_cookie(self, mock_api, monkeypatch, dont_open_a_browser):
        log_in(mock_api, monkeypatch, expires=time.time() + 7 * 24 * 3600)

        assert dont_open_a_browser == [AUTHORIZE_URL]
        assert auth.session_info(BASE_URL)["expired"] is False

    def test_the_client_starts_the_flow_so_it_holds_the_nonce(self, mock_api, monkeypatch):
        # The authorize URL handed to the browser must be the one *this* session was given, or
        # the load balancer will not honour the callback it comes back with.
        mock_api.add(
            mock_api.GET,
            f"{BASE_URL}/openapi.json",
            status=302,
            headers={"Location": AUTHORIZE_URL, "Set-Cookie": "AWSALBAuthNonce=nonce-value; Path=/"},
        )
        callback_succeeds(mock_api)
        authenticated(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)

        auth.login(BASE_URL)

        replayed = next(call.request for call in mock_api.calls if "idpresponse" in call.request.url)
        assert "AWSALBAuthNonce=nonce-value" in replayed.headers["Cookie"]

    def test_rejects_a_callback_url_from_another_host(self, mock_api, monkeypatch):
        bounce(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: "https://evil.example.com/?code=stolen")
        monkeypatch.setattr(auth, "_ask_secret", lambda label: (_ for _ in ()).throw(AssertionError("fell back")))

        with pytest.raises(AssertionError, match="fell back"):
            auth.login(BASE_URL)

        assert not [call for call in mock_api.calls if "evil.example.com" in call.request.url]

    def test_rejects_a_url_carrying_no_code(self, mock_api, monkeypatch):
        bounce(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: f"{BASE_URL}/openapi.json")
        monkeypatch.setattr(auth, "_ask_secret", lambda label: (_ for _ in ()).throw(AssertionError("fell back")))

        with pytest.raises(AssertionError, match="fell back"):
            auth.login(BASE_URL)

    def test_falls_back_to_the_cookie_when_the_code_was_already_spent(self, mock_api, monkeypatch):
        bounce(mock_api)
        # The load balancer spent the code for the browser, so the replay sets no cookie.
        mock_api.add(mock_api.GET, f"{BASE_URL}/oauth2/idpresponse", status=401, body="401")
        authenticated(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)
        monkeypatch.setattr(auth, "_ask_secret", lambda label: "pasted-cookie-value")

        auth.login(BASE_URL)

        session = requests.Session()
        auth.load_session(BASE_URL, session)
        assert session.cookies.get("AWSELBAuthSessionCookie-0") == "pasted-cookie-value"

    def test_a_pasted_cookie_that_is_not_accepted_is_reported(self, mock_api, monkeypatch):
        bounce(mock_api)
        mock_api.add(mock_api.GET, f"{BASE_URL}/oauth2/idpresponse", status=401, body="401")
        bounce(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)
        monkeypatch.setattr(auth, "_ask_secret", lambda label: "truncated")

        with pytest.raises(LakehouseAuthError, match="was not accepted"):
            auth.login(BASE_URL)

        assert auth.session_info(BASE_URL) is None

    def test_nothing_is_cached_when_the_login_does_not_take(self, mock_api, monkeypatch):
        bounce(mock_api)
        callback_succeeds(mock_api)
        bounce(mock_api)  # the verification probe is still redirected
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)

        with pytest.raises(LakehouseAuthError, match="was not accepted"):
            auth.login(BASE_URL)

        assert auth.session_info(BASE_URL) is None

    def test_refuses_when_the_api_asks_for_no_login(self, mock_api):
        authenticated(mock_api)

        with pytest.raises(LakehouseAuthError, match="nothing to log in to"):
            auth.login(BASE_URL)


class TestStoredSession:
    def test_the_cached_cookie_is_sent_on_a_later_request(self, mock_api, monkeypatch):
        log_in(mock_api, monkeypatch)

        # What a later process does: install the cached cookies, then just query. Reading the
        # file back is not enough — the cookie has to survive as one the jar will actually send.
        session = requests.Session()
        assert auth.load_session(BASE_URL, session) is True
        mock_api.add(mock_api.GET, f"{BASE_URL}/query/schema", status=200, json={"ok": True})
        session.get(f"{BASE_URL}/query/schema")

        assert "AWSELBAuthSessionCookie-0=session-value" in mock_api.calls[-1].request.headers["Cookie"]

    def test_expired_cookies_are_not_reused(self, mock_api, monkeypatch, session_file):
        log_in(mock_api, monkeypatch, expires=time.time() + 7 * 24 * 3600)

        # What a week-old session file looks like. It cannot be produced by logging in:
        # `requests` drops an already-expired Set-Cookie instead of storing it.
        store = json.loads(session_file.read_text())
        for cookie in store["sessions"][BASE_URL]["cookies"]:
            cookie["expires"] = time.time() - 60
        session_file.write_text(json.dumps(store))

        session = requests.Session()
        assert auth.load_session(BASE_URL, session) is False
        assert not len(session.cookies)
        assert auth.session_info(BASE_URL)["expired"]

    def test_nothing_stored_for_an_unknown_api(self):
        assert auth.session_info("https://other.example.com") is None
        assert auth.load_session("https://other.example.com", requests.Session()) is False

    def test_clear_removes_only_the_named_api(self, mock_api, monkeypatch):
        log_in(mock_api, monkeypatch)

        assert auth.clear_session(BASE_URL) is True
        assert auth.clear_session(BASE_URL) is False
        assert auth.session_info(BASE_URL) is None

    def test_a_corrupt_store_is_treated_as_empty(self, session_file):
        session_file.write_text("not json at all")

        assert auth.session_info(BASE_URL) is None


class TestConnectorAuthentication:
    def test_a_bounced_request_logs_in_and_retries(self, mock_api, monkeypatch):
        monkeypatch.setattr(auth, "_interactive", lambda: True)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)

        # The first request is bounced to the IdP, then the login flow's own probe is bounced
        # too, and the retry after logging in succeeds.
        bounce(mock_api)
        mock_api.add(mock_api.GET, AUTHORIZE_URL, status=200, body="<html>sign in</html>")
        bounce(mock_api)
        callback_succeeds(mock_api)
        authenticated(mock_api)

        assert connector.get("/openapi.json") == {"openapi": "3.1.0"}
        assert auth.session_info(BASE_URL) is not None

    def test_says_how_to_log_in_when_there_is_no_terminal(self, mock_api, monkeypatch):
        monkeypatch.setattr(auth, "_interactive", lambda: False)
        bounce(mock_api)
        mock_api.add(mock_api.GET, AUTHORIZE_URL, status=200, body="<html>sign in</html>")

        with pytest.raises(LakehouseAuthError, match="psr-lakehouse login"):
            connector.get("/openapi.json")

    def test_auto_login_can_be_turned_off(self, mock_api, monkeypatch):
        monkeypatch.setenv("LAKEHOUSE_AUTO_LOGIN", "0")
        bounce(mock_api)
        mock_api.add(mock_api.GET, AUTHORIZE_URL, status=200, body="<html>sign in</html>")

        with pytest.raises(LakehouseAuthError, match="LAKEHOUSE_AUTO_LOGIN is off"):
            connector.get("/openapi.json")

    def test_a_rejected_account_is_not_a_login_problem(self, mock_api):
        mock_api.add(mock_api.GET, f"{BASE_URL}/query/schema", status=403, json={"detail": "Forbidden"})

        with pytest.raises(LakehouseAuthError, match="rejected this account"):
            connector.get("/query/schema")

    def test_an_authenticated_request_is_untouched(self, mock_api):
        authenticated(mock_api)

        assert connector.get("/openapi.json") == {"openapi": "3.1.0"}
