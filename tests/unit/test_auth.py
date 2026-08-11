import json
import stat
import time

import pytest
import requests

from psr.lakehouse import auth
from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseAuthError, LakehouseError

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


class TestLoginRejections:
    """Inputs that reach the flow from somewhere other than the user typing them."""

    def test_logging_in_again_when_a_session_is_already_held(self, mock_api, monkeypatch):
        # `CookieJar.clear(name=…)` raises unless given the domain and path too, so clearing the
        # previous cookie used to abort every re-login.
        session = requests.Session()
        session.cookies.set_cookie(
            requests.cookies.create_cookie(
                name="AWSELBAuthSessionCookie-0", value="stale", domain="test-api.example.com"
            )
        )
        bounce(mock_api)
        callback_succeeds(mock_api)
        authenticated(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)

        auth.login(BASE_URL, session=session)

        assert session.cookies.get("AWSELBAuthSessionCookie-0") == "session-value"

    def test_refuses_to_open_a_redirect_that_is_not_a_web_address(self, mock_api, dont_open_a_browser):
        # Handed straight to the OS URL handler, so a `Location` naming another scheme is not
        # something to launch. It arrives from the network, not from the user.
        mock_api.add(
            mock_api.GET,
            f"{BASE_URL}/openapi.json",
            status=302,
            headers={"Location": "javascript:alert(1)"},
        )

        with pytest.raises(LakehouseAuthError, match="not a web address"):
            auth.login(BASE_URL)

        assert dont_open_a_browser == []

    def test_rejects_a_callback_url_that_downgrades_to_http(self, mock_api, monkeypatch):
        # Same host, but cleartext: replaying it would put the authorization code on the wire.
        bounce(mock_api)
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL.replace("https://", "http://"))
        monkeypatch.setattr(auth, "_ask_secret", lambda label: (_ for _ in ()).throw(AssertionError("fell back")))

        with pytest.raises(AssertionError, match="fell back"):
            auth.login(BASE_URL)

        assert not [call for call in mock_api.calls if call.request.url.startswith("http://")]

    def test_a_session_the_server_refuses_is_not_a_successful_login(self, mock_api, monkeypatch):
        # Past the load balancer, refused by the application: not something to cache and call done.
        bounce(mock_api)
        callback_succeeds(mock_api)
        mock_api.add(mock_api.GET, f"{BASE_URL}/openapi.json", status=403, json={"detail": "Forbidden"})
        monkeypatch.setattr(auth, "_ask", lambda label: CALLBACK_URL)

        with pytest.raises(LakehouseAuthError, match="refused the account"):
            auth.login(BASE_URL)

        assert auth.session_info(BASE_URL) is None

    def test_the_pasted_cookie_is_scoped_without_the_port(self, mock_api, monkeypatch):
        # A cookie domain may not carry a port; one that does is stored and then never sent.
        based = "https://test-api.example.com:8443"
        mock_api.add(mock_api.GET, f"{based}/openapi.json", status=302, headers={"Location": AUTHORIZE_URL})
        mock_api.add(mock_api.GET, f"{based}/oauth2/idpresponse", status=401, body="401")
        mock_api.add(mock_api.GET, f"{based}/openapi.json", status=200, json={"openapi": "3.1.0"})
        monkeypatch.setattr(auth, "_ask", lambda label: f"{based}/oauth2/idpresponse?code=c&state=xyz")
        monkeypatch.setattr(auth, "_ask_secret", lambda label: "hand-copied")

        session = requests.Session()
        auth.login(based, session=session)

        assert session.cookies.get("AWSELBAuthSessionCookie-0") == "hand-copied"
        mock_api.add(mock_api.GET, f"{based}/query/schema", status=200, json={"ok": True})
        session.get(f"{based}/query/schema")
        assert "AWSELBAuthSessionCookie-0=hand-copied" in mock_api.calls[-1].request.headers["Cookie"]


class TestSessionFilePermissions:
    def test_the_session_file_is_not_world_readable(self, mock_api, monkeypatch, session_file):
        log_in(mock_api, monkeypatch)

        assert stat.S_IMODE(session_file.stat().st_mode) == 0o600

    def test_a_loose_leftover_temp_file_cannot_donate_its_mode(self, mock_api, monkeypatch, session_file):
        # The credential must never touch the disk at a readable mode, not even briefly, so the
        # temp file is recreated rather than truncated in place.
        tmp = session_file.with_name(f"{session_file.name}.tmp")
        tmp.write_text("{}")
        tmp.chmod(0o666)

        log_in(mock_api, monkeypatch)

        assert stat.S_IMODE(session_file.stat().st_mode) == 0o600

    def test_a_directory_it_did_not_create_is_left_alone(self, mock_api, monkeypatch, tmp_path):
        # LAKEHOUSE_SESSION_FILE is user-set; its parent may be shared and is not ours to tighten.
        shared = tmp_path / "shared"
        shared.mkdir(mode=0o755)
        monkeypatch.setenv("LAKEHOUSE_SESSION_FILE", str(shared / "session.json"))

        log_in(mock_api, monkeypatch)

        assert stat.S_IMODE(shared.stat().st_mode) == 0o755

    def test_a_directory_it_creates_is_private(self, mock_api, monkeypatch, tmp_path):
        monkeypatch.setenv("LAKEHOUSE_SESSION_FILE", str(tmp_path / "made-by-us" / "session.json"))

        log_in(mock_api, monkeypatch)

        assert stat.S_IMODE((tmp_path / "made-by-us").stat().st_mode) == 0o700


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

    @pytest.mark.parametrize(
        "cookies",
        [
            [{"value": "no-name"}],
            [{"name": "AWSELBAuthSessionCookie-0"}],
            [{"name": 1, "value": 2}],
            ["not-a-dict"],
            "not-a-list",
        ],
        ids=["no-name", "no-value", "wrong-types", "not-a-dict", "not-a-list"],
    )
    def test_a_malformed_entry_reads_as_logged_out_rather_than_raising(self, session_file, cookies):
        # The file is hand-editable and can be truncated, and `initialize()` loads it — a bad shape
        # must not turn into a KeyError that breaks every fetch.
        session_file.write_text(json.dumps({"version": 1, "sessions": {BASE_URL: {"cookies": cookies}}}))

        assert auth.load_session(BASE_URL, requests.Session()) is False
        assert auth.session_info(BASE_URL) == {"saved_at": None, "expires_at": None, "expired": False}

    def test_an_unparseable_expiry_does_not_break_the_summary(self, session_file):
        session_file.write_text(
            json.dumps(
                {
                    "version": 1,
                    "sessions": {
                        BASE_URL: {"cookies": [{"name": "AWSELBAuthSessionCookie-0", "value": "v", "expires": "soon"}]}
                    },
                }
            )
        )

        assert auth.session_info(BASE_URL)["expires_at"] is None
        assert auth.load_session(BASE_URL, requests.Session()) is True


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


class TestConnectorLoginAndLogout:
    def test_login_honours_an_explicit_base_url(self, mock_api, monkeypatch):
        # The connector is a singleton and the autouse fixture has already pointed it at BASE_URL,
        # so an explicit argument has to win rather than being quietly dropped.
        other = "https://other-api.example.com"
        logged_into = []
        monkeypatch.setattr(auth, "login", lambda url, session=None: logged_into.append(url))
        mock_api.add(mock_api.GET, f"{other}/health-check", status=200, json=True)

        connector.login(base_url=other)

        assert logged_into == [other]

    def test_logout_does_not_need_the_api_to_be_reachable(self, mock_api, monkeypatch):
        # Throwing away a credential must not depend on a health check — being unable to reach the
        # API is often the reason for logging out in the first place.
        log_in(mock_api, monkeypatch)
        connector._is_initialized = False

        assert connector.logout(base_url=BASE_URL) is True
        assert auth.session_info(BASE_URL) is None
        assert not [call for call in mock_api.calls if "health-check" in call.request.url]

    def test_logout_falls_back_to_the_url_it_was_last_pointed_at(self, mock_api, monkeypatch):
        log_in(mock_api, monkeypatch)
        connector._is_initialized = False  # the URL it was given is still remembered

        assert connector.logout() is True
        assert auth.session_info(BASE_URL) is None

    def test_logout_says_so_when_there_is_no_url_at_all(self, monkeypatch):
        connector._is_initialized = False
        monkeypatch.delattr(connector, "_base_url", raising=False)
        monkeypatch.delenv("LAKEHOUSE_API_URL", raising=False)

        with pytest.raises(LakehouseError, match="No API URL to log out of"):
            connector.logout()
