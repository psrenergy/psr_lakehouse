"""Browser login for a lakehouse deployment behind the ALB's Cognito authentication.

Requests to a deployment behind that load balancer never reach the application unless it
recognises the caller: its `authenticate-cognito` rule answers every unauthenticated request
with a `302` to the Cognito managed login page, which is why an unauthenticated client sees
HTML where it expected JSON.

The only credential that load balancer accepts is the `AWSELBAuthSessionCookie-*` pair it sets
itself, at the end of an OAuth2 code flow whose `redirect_uri` is fixed to
`https://<host>/oauth2/idpresponse`. There is no bearer token, no API key, and no loopback
callback a CLI could listen on — an `Authorization` header changes nothing, the request is
still bounced. So signing in happens in a browser, and this module's job is to get the
resulting cookie *here*.

That last part is the whole difficulty, and it explains the shape of `login`. The flow must be
started by this client, not by the browser: `_start_flow` collects the `AWSALBAuthNonce` cookie
the load balancer issues, and the callback at the end is only honoured for whoever holds it.
The browser therefore signs the user in and then stops on a `401` at a URL that still carries
an unspent authorization code, which the user pastes back so `_finish_from_callback` can redeem
it from here. Were the browser allowed to run the flow end to end instead, it would be the
browser that ended up holding the session — no use to a Python process.

This works because the load balancer validates the nonce *before* it spends the code, which is
undocumented but confirmed against production: the browser's rejected callback leaves the code
untouched for us. `_paste_cookie` stays as the fallback should that order ever change — the
cookie is then copied out of the browser by hand, which is clumsier but cannot be defeated by
any of this.

The session is cached in `~/.psr-lakehouse/session.json`, so this is a weekly event rather than
a per-script one.
"""

import getpass
import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from urllib.parse import urlparse

import requests

from psr.lakehouse.exceptions import LakehouseAuthError

# Cheap, always-present, and *protected* — unlike `/health-check`, which has its own ALB rule
# that forwards without authentication and so never reveals whether we are logged in.
_PROBE_PATH = "/openapi.json"

# The load balancer splits its session cookie across `-0`, `-1`, ... when the claims are large,
# so this is a prefix rather than a name.
_ALB_COOKIE_PREFIX = "AWSELBAuthSessionCookie"

_TIMEOUT = 30

# The load balancer does not tell us its session timeout, so a cookie we install by hand is
# stamped with the ALB default of a week. Guessing long is harmless: a dead cookie is simply
# bounced, which starts a fresh login.
_ASSUMED_SESSION_SECONDS = 7 * 24 * 3600


# --------------------------------------------------------------------------- #
# Stored session
# --------------------------------------------------------------------------- #
def session_file() -> Path:
    """Path of the file holding the cached load-balancer cookies."""
    override = os.getenv("LAKEHOUSE_SESSION_FILE")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".psr-lakehouse" / "session.json"


def _read_store() -> dict:
    """Read the whole store, treating anything unreadable or corrupt as "no sessions"."""
    try:
        store = json.loads(session_file().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": 1, "sessions": {}}
    if not isinstance(store, dict) or not isinstance(store.get("sessions"), dict):
        return {"version": 1, "sessions": {}}
    return store


def _write_store(store: dict) -> None:
    path = session_file()

    # Only a directory this created is re-permissioned. `LAKEHOUSE_SESSION_FILE` is a documented,
    # user-set path, so its parent may be a directory that already exists for other reasons and is
    # not ours to tighten.
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        _restrict(path.parent, 0o700)

    # Written to a sibling and renamed so an interrupted write cannot leave a half-written file
    # behind. Opened 0600 *before* the credential goes in — writing first and chmod-ing after
    # would leave it world-readable (0644 under the usual umask) for the length of the write, and
    # unlinking first means a pre-existing temp file cannot donate a looser mode through O_CREAT.
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.unlink(missing_ok=True)
    descriptor = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
        json.dump(store, handle, indent=2)

    # `replace` carries the temp file's inode, and with it the 0600, over the destination.
    tmp.replace(path)


def _restrict(path: Path, mode: int) -> None:
    """Best-effort permission tightening — a no-op where the OS does not honour it."""
    try:
        path.chmod(mode)
    except OSError:
        pass


def _store_key(base_url: str) -> str:
    return base_url.rstrip("/")


def save_session(base_url: str, session: requests.Session) -> None:
    """Persist the load-balancer cookies held by `session` for `base_url`."""
    cookies = [
        {
            "name": cookie.name,
            "value": cookie.value,
            "domain": cookie.domain,
            "path": cookie.path,
            "expires": cookie.expires,
            "secure": bool(cookie.secure),
        }
        for cookie in session.cookies
        if cookie.name.startswith(_ALB_COOKIE_PREFIX)
    ]
    if not cookies:
        raise LakehouseAuthError(
            f"Login finished but {base_url} never set a {_ALB_COOKIE_PREFIX} cookie, so there is "
            "no session to keep. Is this deployment really behind the load balancer?"
        )

    store = _read_store()
    store["sessions"][_store_key(base_url)] = {"saved_at": int(time.time()), "cookies": cookies}
    _write_store(store)


def _stored_cookies(entry: object) -> list[dict]:
    """The well-formed cookie entries in a stored session, ignoring anything else.

    The file is on disk and hand-editable, and a truncated or edited one must degrade to "not
    logged in" — not raise a `KeyError` out of `initialize()` and break every fetch.
    """
    if not isinstance(entry, dict) or not isinstance(entry.get("cookies"), list):
        return []

    valid = []
    for cookie in entry["cookies"]:
        if not isinstance(cookie, dict):
            continue
        if not isinstance(cookie.get("name"), str) or not isinstance(cookie.get("value"), str):
            continue
        if not isinstance(cookie.get("expires"), (int, float, type(None))):
            cookie = {**cookie, "expires": None}
        valid.append(cookie)
    return valid


def load_session(base_url: str, session: requests.Session) -> bool:
    """Install the cached cookies for `base_url` onto `session`; say whether any were usable.

    Expired cookies are dropped rather than sent, so a week-old session behaves like no session
    at all instead of provoking a redirect on the first real request.
    """
    now = time.time()
    installed = 0
    for cookie in _stored_cookies(_read_store()["sessions"].get(_store_key(base_url))):
        expires = cookie.get("expires")
        if expires and expires <= now:
            continue
        session.cookies.set_cookie(
            requests.cookies.create_cookie(
                name=cookie["name"],
                value=cookie["value"],
                domain=cookie.get("domain") if isinstance(cookie.get("domain"), str) else "",
                path=cookie.get("path") if isinstance(cookie.get("path"), str) else "/",
                expires=expires,
                secure=bool(cookie.get("secure", True)),
            )
        )
        installed += 1

    return bool(installed)


def session_info(base_url: str) -> dict | None:
    """Describe the cached session for `base_url`, or `None` when there is none."""
    entry = _read_store()["sessions"].get(_store_key(base_url))
    if not entry:
        return None

    expiries = [cookie["expires"] for cookie in _stored_cookies(entry) if cookie.get("expires")]
    return {
        "saved_at": entry.get("saved_at") if isinstance(entry, dict) else None,
        "expires_at": min(expiries) if expiries else None,
        "expired": bool(expiries) and min(expiries) <= time.time(),
    }


def clear_session(base_url: str | None = None) -> bool:
    """Forget the cached session for `base_url`, or every cached session when it is `None`."""
    store = _read_store()
    if base_url is None:
        removed = bool(store["sessions"])
        store["sessions"] = {}
    else:
        removed = store["sessions"].pop(_store_key(base_url), None) is not None
    if removed:
        _write_store(store)
    return removed


def _clear_alb_cookies(session: requests.Session) -> None:
    # `CookieJar.clear(name=…)` on its own raises: it demands the domain and path as well, and
    # `requests` does not override it. This helper does that bookkeeping for every match.
    for name in [cookie.name for cookie in session.cookies if cookie.name.startswith(_ALB_COOKIE_PREFIX)]:
        requests.cookies.remove_cookie_by_name(session.cookies, name)


def _has_alb_cookie(session: requests.Session) -> bool:
    return any(cookie.name.startswith(_ALB_COOKIE_PREFIX) for cookie in session.cookies)


# --------------------------------------------------------------------------- #
# Recognising the bounce to the identity provider
# --------------------------------------------------------------------------- #
def _host(url: str) -> str:
    """Host *and port*, for comparing one URL against another like for like."""
    return urlparse(url).netloc.lower()


def _hostname(url: str) -> str:
    """Host without the port, which is the only form a cookie domain may take."""
    return (urlparse(url).hostname or "").lower()


def _origin(url: str) -> tuple[str, str]:
    return urlparse(url).scheme.lower(), _host(url)


def bounced_to_idp(response: requests.Response, base_url: str) -> bool:
    """Did this response come from the identity provider instead of the lakehouse?

    `requests` follows the ALB's redirect for us, so an unauthenticated request quietly ends up
    on the Cognito domain with a `200` and a page of HTML. Comparing the host of the *final* URL
    is what tells the two apart — the status code alone does not.
    """
    return _host(response.url) != _host(base_url)


# --------------------------------------------------------------------------- #
# Terminal interaction
# --------------------------------------------------------------------------- #
def _interactive() -> bool:
    try:
        return sys.stdin.isatty()
    except (AttributeError, ValueError):
        return False


def note(message: str) -> None:
    """Report login progress on stderr, so it never lands in a redirected data stream."""
    print(message, file=sys.stderr, flush=True)


def _require_interactive() -> None:
    if _interactive():
        return
    raise LakehouseAuthError(
        "Logging in needs a browser and a terminal to paste into, and there is none here. Run "
        "`psr-lakehouse login` from a terminal first — the session is cached, so unattended runs "
        "after that work on their own (point LAKEHOUSE_SESSION_FILE at the cached session if it "
        "lives elsewhere)."
    )


def _ask(label: str) -> str:
    _require_interactive()
    answer = input(f"{label}: ").strip()
    if not answer:
        raise LakehouseAuthError(f"No {label.lower()} given; login aborted.")
    return answer


def _ask_secret(label: str) -> str:
    _require_interactive()
    answer = getpass.getpass(f"{label}: ")
    if not answer:
        raise LakehouseAuthError(f"No {label.lower()} given; login aborted.")
    return answer


def _open_browser(url: str) -> None:
    """Best-effort browser launch; the URL is printed regardless, so failure is not fatal."""
    # Under WSL the registered opener is a Linux one (`gio`) that cannot reach the Windows
    # browser, so hand the URL to Windows directly. `explorer.exe` reports a non-zero exit even
    # when it succeeds, hence `check=False` and no attempt to interpret the result.
    if _is_wsl():
        try:
            subprocess.run(["explorer.exe", url], check=False, capture_output=True, timeout=15)
            return
        except (OSError, subprocess.SubprocessError):
            pass

    try:
        webbrowser.open(url)
    except webbrowser.Error:
        pass


def _is_wsl() -> bool:
    if os.getenv("WSL_DISTRO_NAME"):
        return True
    try:
        return "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower()
    except OSError:
        return False


# --------------------------------------------------------------------------- #
# The login flow
# --------------------------------------------------------------------------- #
def login(base_url: str, session: requests.Session | None = None) -> None:
    """Sign in in a browser and cache the resulting load-balancer session.

    Any sign-in method the user pool offers works, because the browser is what performs it:
    password, Google, a passkey, MFA.

    Args:
        base_url: Lakehouse base URL, e.g. `https://api.example.com`.
        session: Session to authenticate and take the cookies from. A throwaway one is used when
            omitted; the cached cookies are the point either way.

    Raises:
        LakehouseAuthError: The login could not be completed.
    """
    base_url = base_url.rstrip("/")
    session = session if session is not None else requests.Session()
    authorize_url = _start_flow(session, base_url)

    _open_browser(authorize_url)

    # Printed whether or not opening worked: a browser that fails to launch is common enough (a
    # remote shell, WSL without a desktop session) that hiding the URL would strand the user.
    note("")
    note("Sign in in your browser — password, Google, a passkey, whatever the account uses:")
    note(f"  {authorize_url}")
    note("")
    note(f"It ends on a '401 Authorization Required' page at {_host(base_url)}. That is expected")
    note("and means the sign-in worked: the load balancer will only spend it for whoever started")
    note("the flow, which is this client. Copy that page's URL out of the address bar.")
    note("")

    pasted = _ask("URL from the address bar")
    hint = "The login did not take."
    try:
        _finish_from_callback(session, base_url, pasted)
    except LakehouseAuthError as exc:
        note("")
        note(f"That callback did not complete the login: {exc.message}")
        _paste_cookie(session, base_url)
        hint = f"Check that you copied the value of {_ALB_COOKIE_PREFIX}-0 in full."

    _verify(session, base_url, hint)
    save_session(base_url, session)
    note(f"Logged in to {base_url}.")


def _start_flow(session: requests.Session, base_url: str) -> str:
    """Ask the lakehouse for a login and return the authorize URL it points us at.

    This is the step that makes the rest possible: the load balancer answers with a `302` *and*
    an `AWSALBAuthNonce` cookie, which lands in `session`. That nonce is what binds the flow to
    this client, and why the browser cannot be left to complete the flow on its own behalf.
    """
    # A stale cookie would make the probe look authenticated and skip the whole flow, which is
    # the opposite of what an explicit login should do.
    _clear_alb_cookies(session)

    try:
        probe = session.get(f"{base_url}{_PROBE_PATH}", allow_redirects=False, timeout=_TIMEOUT)
    except requests.RequestException as exc:
        raise LakehouseAuthError(f"Could not reach {base_url}: {exc}") from exc

    authorize_url = probe.headers.get("location", "") if probe.is_redirect else ""
    if not authorize_url or _host(authorize_url) == _host(base_url):
        raise LakehouseAuthError(
            f"{base_url} answered HTTP {probe.status_code} without redirecting to an identity "
            "provider, so it is not behind the load balancer's Cognito authentication and there "
            "is nothing to log in to."
        )

    # This URL is handed to the operating system's URL handler, which will act on whatever scheme
    # it is given. It arrives in a `Location` header, so it is only as trustworthy as the host in
    # `base_url` — check it is an ordinary web address before opening it.
    if urlparse(authorize_url).scheme.lower() not in ("http", "https"):
        raise LakehouseAuthError(
            f"{base_url} redirected the login to something that is not a web address; refusing to "
            f"open it: {authorize_url[:80]}"
        )

    note(f"Logging in to {base_url} via {_host(authorize_url)}")
    return authorize_url


def _finish_from_callback(session: requests.Session, base_url: str, pasted: str) -> None:
    """Replay the browser's callback URL from here, where the nonce cookie is."""
    pasted = pasted.strip()
    parsed = urlparse(pasted)

    # The full origin, not just the host: matching on the host alone would accept an `http://`
    # paste and replay the authorization code over cleartext.
    if _origin(pasted) != _origin(base_url):
        raise LakehouseAuthError(f"that is not a {urlparse(base_url).scheme}://{_host(base_url)} URL")
    if "code=" not in (parsed.query or ""):
        raise LakehouseAuthError("that URL carries no authorization code, so the sign-in did not finish")

    try:
        session.get(pasted, timeout=_TIMEOUT)
    except requests.RequestException as exc:
        raise LakehouseAuthError(f"replaying the callback failed: {exc}") from exc

    if not _has_alb_cookie(session):
        raise LakehouseAuthError("the load balancer refused to exchange the code (it was probably already spent)")


def _paste_cookie(session: requests.Session, base_url: str) -> None:
    """Last resort: take the session cookie the browser already holds, by hand.

    Nothing can stop this from working — the browser completed the flow, so it has the cookie —
    at the cost of asking for a few clicks in the developer tools.
    """
    note("")
    note("Falling back to copying the session cookie out of the browser instead:")
    note(f"  1. Open {base_url}{_PROBE_PATH} in the browser — you should see JSON, not a login page.")
    note("  2. Open the developer tools (F12) → Application (or Storage) → Cookies →")
    note(f"     {base_url}")
    note(f"  3. Copy the *value* of {_ALB_COOKIE_PREFIX}-0.")
    note("")

    value = _ask_secret(f"{_ALB_COOKIE_PREFIX}-0 value")
    session.cookies.set_cookie(
        requests.cookies.create_cookie(
            name=f"{_ALB_COOKIE_PREFIX}-0",
            value=value.strip(),
            # `hostname`, not `netloc`: a domain carrying a port matches nothing, so the cookie
            # would be stored and then never sent.
            domain=_hostname(base_url),
            path="/",
            expires=int(time.time() + _ASSUMED_SESSION_SECONDS),
            secure=True,
        )
    )


def _verify(session: requests.Session, base_url: str, hint: str) -> None:
    """Confirm the session actually gets through before it is written to disk."""
    try:
        probe = session.get(f"{base_url}{_PROBE_PATH}", allow_redirects=False, timeout=_TIMEOUT)
    except requests.RequestException as exc:
        raise LakehouseAuthError(f"Could not confirm the login against {base_url}: {exc}") from exc

    if probe.is_redirect:
        raise LakehouseAuthError(
            f"The session was not accepted — requests are still redirected to the login page. {hint}"
        )

    # Getting past the load balancer is not the same as being allowed in: the application applies
    # its own rule (a verified email in an allowed domain) and answers 403. Saying "logged in" here
    # would cache a session that cannot fetch anything and move the complaint to the first query.
    if probe.status_code == 403:
        raise LakehouseAuthError(
            f"Signed in, but {base_url} refused the account (HTTP 403). Access requires a verified "
            "email in an allowed domain — sign in as a different user."
        )


def ensure_login(session: requests.Session, base_url: str) -> None:
    """Log in because a request was bounced, unless the caller opted out of that."""
    if os.getenv("LAKEHOUSE_AUTO_LOGIN", "1").strip().lower() in ("0", "false", "no"):
        raise LakehouseAuthError(
            f"Not logged in to {base_url} and LAKEHOUSE_AUTO_LOGIN is off. Run `psr-lakehouse login`."
        )

    _require_interactive()
    note(f"Not logged in to {base_url}.")
    login(base_url, session=session)
