"""Command line entry point: `psr-lakehouse whoami`.

Checking which account a token belongs to is the one thing worth doing outside a
script, because the answer decides whether running the script is worth starting.
It is deliberately the whole CLI: authentication is an environment variable now,
so there is no session to create or forget.
"""

import argparse
import os
import sys

from psr.lakehouse.connector import connector
from psr.lakehouse.exceptions import LakehouseError


def _resolve_url(url: str | None) -> str:
    resolved = url or os.getenv("LAKEHOUSE_API_URL")
    if not resolved:
        raise LakehouseError("No API URL given. Pass --url or set the LAKEHOUSE_API_URL environment variable.")
    return resolved.rstrip("/")


def _whoami(args: argparse.Namespace) -> int:
    url = _resolve_url(args.url)
    connector.initialize(base_url=url)
    identity = connector.whoami()

    subscription = identity.get("subscription")
    print(f"{identity.get('full_name') or 'Unknown'} <{identity.get('email')}>")
    print(f"Plan: {subscription['name'] if subscription else 'none'}")
    print(f"API:  {url}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="psr-lakehouse", description="PSR Lakehouse client.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    whoami = subcommands.add_parser("whoami", help="Show which account the configured token belongs to.")
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
