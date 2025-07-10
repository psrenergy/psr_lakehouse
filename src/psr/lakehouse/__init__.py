from .client import client
from .connector import connector as connector

from .aliases import ccee as ccee
from .aliases import ons as ons

def set_credentials(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_region_name: str | None = None,
):
    connector.Connector.set_credentials(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        aws_region_name=aws_region_name,
    )


__all__ = ["client", "set_credentials"]

