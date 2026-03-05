from .alias import register_aliases
from .client import client
from .connector import connector as connector
from .metadata import get_model_name

initialize = connector.initialize

register_aliases()

__all__ = [
    "client",
    "connector",
    "initialize",
    "get_model_name",
]
