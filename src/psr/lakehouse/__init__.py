from .aliases import ccee as ccee, ons as ons
from .client import client
from .connector import connector as connector
from .metadata import metadata_registry

initialize = connector.initialize

__all__ = ["client", "connector", "initialize", "ccee", "ons", "metadata_registry"]
