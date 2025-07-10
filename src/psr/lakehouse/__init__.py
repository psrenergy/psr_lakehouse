from .client import client
from .connector import connector as connector

from .aliases import ccee as ccee
from .aliases import ons as ons


def initialize(
    aws_access_key_id: str,
    aws_secret_access_key: str,
):
    connector.initialize(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


__all__ = ["client", "initialize"]
