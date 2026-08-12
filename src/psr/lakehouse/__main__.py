"""Command line entry point: `psr-lakehouse login | logout | whoami`.

Logging in is a one-off act that outlives the process doing it — the session is cached on disk —
so it belongs on the command line rather than inside every script. Scripts do still start a login
on demand (see `psr.lakehouse.auth`), but running `psr-lakehouse login` once keeps the browser
detour out of the middle of a data fetch.
"""

import argparse
import os
import sys
from datetime import datetime, timezone

from psr.lakehouse import auth
from psr.lakehouse.exceptions import LakehouseError


def _resolve_url(url: str | None) -> str:
    resolved = url or os.getenv("LAKEHOUSE_API_URL")
    if not resolved:
        raise LakehouseError("No API URL given. Pass --url or set the LAKEHOUSE_API_URL environment variable.")
    return resolved.rstrip("/")


def _format_timestamp(value: int | float | None) -> str:
    if not value:
        return "unknown"
    return datetime.fromtimestamp(value, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")


def _login(args: argparse.Namespace) -> int:
    auth.login(_resolve_url(args.url))
    return 0


def _logout(args: argparse.Namespace) -> int:
    url = None if args.all else _resolve_url(args.url)
    if auth.clear_session(url):
        print(f"Logged out of {url}." if url else "Logged out of every lakehouse.")
    else:
        print(f"No cached session for {url}." if url else "No cached sessions.")
    return 0


def _whoami(args: argparse.Namespace) -> int:
    url = _resolve_url(args.url)
    info = auth.session_info(url)
    if not info:
        print(f"Not logged in to {url}.")
        return 1

    state = "expired" if info["expired"] else f"valid until {_format_timestamp(info['expires_at'])}"
    who = f" as {info['email']}" if info.get("email") else ""
    print(f"Logged in to {url}{who} ({state})")
    print(f"Session cached in {auth.session_file()}")
    return 1 if info["expired"] else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="psr-lakehouse", description="PSR Lakehouse client.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    login = subcommands.add_parser("login", help="Sign in in a browser and cache the session.")
    login.add_argument("--url", help="API base URL. Defaults to $LAKEHOUSE_API_URL.")
    login.set_defaults(handler=_login)

    logout = subcommands.add_parser("logout", help="Forget the cached session.")
    logout.add_argument("--url", help="API base URL. Defaults to $LAKEHOUSE_API_URL.")
    logout.add_argument("--all", action="store_true", help="Forget every cached session.")
    logout.set_defaults(handler=_logout)

    whoami = subcommands.add_parser("whoami", help="Show the cached session, if any.")
    whoami.add_argument("--url", help="API base URL. Defaults to $LAKEHOUSE_API_URL.")
    whoami.set_defaults(handler=_whoami)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except LakehouseError as error:
        print(error, file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nAborted.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
