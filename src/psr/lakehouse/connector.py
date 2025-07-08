import boto3
import os
import sqlalchemy


class Connector:
    _instance = None
    _region: str = "us-east-1"
    _client = boto3.client("rds", region_name="us-east-1")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def engine(self) -> sqlalchemy.Engine:
        user = os.getenv("POSTGRES_USER")
        endpoint = os.getenv("POSTGRES_SERVER")
        port = os.getenv("POSTGRES_PORT")
        dbname = os.getenv("POSTGRES_DB")
        region = self._region

        token = self._client.generate_db_auth_token(
            DBHostname=endpoint,
            Port=port,
            DBUsername=user,
            Region=region,
        )
        connection_string = (
            f"postgresql+psycopg://{user}:{token}@{endpoint}:{port}/{dbname}?sslmode=require&sslrootcert=SSLCERTIFICATE"
        )

        return sqlalchemy.create_engine(connection_string)


connector = Connector()
