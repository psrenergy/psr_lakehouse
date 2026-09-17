from .aliases import register_aliases
from .client import client
from .connector import connector as connector
from .metadata import get_model_name

initialize = connector.initialize
whoami = connector.whoami

register_aliases()

__all__ = [
    "client",
    "connector",
    "initialize",
    "whoami",
    "get_model_name",
]
