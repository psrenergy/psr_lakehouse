from .aliases import ccee as ccee, ons as ons
from .client import client
from .connector import connector as connector


def initialize(
    aws_access_key_id: str,
    aws_secret_access_key: str,
):
    connector.initialize(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


__all__ = ["client", "initialize"]
