from .aliases import register_aliases
from .client import client
from .connector import connector as connector
from .metadata import get_model_name

initialize = connector.initialize
login = connector.login
logout = connector.logout

register_aliases()

__all__ = [
    "client",
    "connector",
    "initialize",
    "login",
    "logout",
    "get_model_name",
]
