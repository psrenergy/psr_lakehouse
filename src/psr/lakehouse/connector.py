from psr.lakehouse.exceptions import LakehouseError

from sqlalchemy import create_engine, Engine


class DatabaseConnector:
    """
    A global database connector that manages database connection parameters and engine.
    
    This class follows the singleton pattern to ensure only one database connection
    is maintained throughout the application lifecycle.
    """
    
    _instance = None
    _engine: Engine | None = None
    _server: str | None = None
    _port: str | None = None
    _db: str | None = None
    _user: str | None = None
    _password: str | None = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def configure(self, server: str, port: str, db: str, user: str, password: str) -> None:
        """
        Configure the database connection parameters.
        
        Args:
            server (str): The database server address.
            port (str): The database server port.
            db (str): The name of the database.
            user (str): The username for authentication.
            password (str): The password for authentication.
        """
        self._server = server
        self._port = port
        self._db = db
        self._user = user
        self._password = password
        
        # Create the engine with the new configuration
        self._create_engine()
    
    def _create_engine(self) -> None:
        """
        Creates the SQLAlchemy engine with the configured parameters.
        
        Raises:
            LakehouseError: If the connector is not configured or if there's an import error.
        """
        if not all([self._server, self._port, self._db, self._user, self._password]):
            raise LakehouseError("Database connector not configured. Call configure() first.")
        
        connection_string = f"postgresql+psycopg://{self._user}:{self._password}@{self._server}:{self._port}/{self._db}"
        
        try:
            self._engine = create_engine(connection_string)
        except ImportError as e:
            raise LakehouseError("SQLAlchemy and psycopg2 are required to use the Lakehouse client.") from e
    
    @property
    def engine(self) -> Engine:
        """
        Get the database engine.
        
        Returns:
            Engine: The SQLAlchemy engine instance.
            
        Raises:
            LakehouseError: If the connector is not configured.
        """
        if self._engine is None:
            raise LakehouseError("Database connector not configured. Call configure() first.")
        return self._engine
    
    @property
    def server(self) -> str:
        """Get the database server address."""
        if self._server is None:
            raise LakehouseError("Database connector not configured. Call configure() first.")
        return self._server
    
    @property
    def port(self) -> str:
        """Get the database server port."""
        if self._port is None:
            raise LakehouseError("Database connector not configured. Call configure() first.")
        return self._port
    
    @property
    def db(self) -> str:
        """Get the database name."""
        if self._db is None:
            raise LakehouseError("Database connector not configured. Call configure() first.")
        return self._db
    
    @property
    def user(self) -> str:
        """Get the database username."""
        if self._user is None:
            raise LakehouseError("Database connector not configured. Call configure() first.")
        return self._user
    
    def is_configured(self) -> bool:
        """
        Check if the connector is configured.
        
        Returns:
            bool: True if the connector is configured, False otherwise.
        """
        return all([self._server, self._port, self._db, self._user, self._password])
    
    def reset(self) -> None:
        """
        Reset the connector configuration and close the engine.
        """
        if self._engine:
            self._engine.dispose()
        
        self._engine = None
        self._server = None
        self._port = None
        self._db = None
        self._user = None
        self._password = None


# Global connector instance
connector = DatabaseConnector()
