import json
import boto3
import sqlalchemy


class Connector:
    _instance = None
    _region: str = "us-east-1"
    _rds = boto3.client("rds", region_name=_region)
    _user: str
    _endpoint: str
    _port: str
    _dbname: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            secrets_manager = boto3.client("secretsmanager", region_name="us-east-1")
            secret_response = secrets_manager.get_secret_value(SecretId="psr-lakehouse-secrets")
            secret = json.loads(secret_response["SecretString"])
            cls._user = secret["POSTGRES_USER"]
            cls._endpoint = secret["POSTGRES_SERVER"]
            cls._port = secret["POSTGRES_PORT"]
            cls._dbname = secret["POSTGRES_DB"]
        return cls._instance

    def engine(self) -> sqlalchemy.Engine:
        token = self._rds.generate_db_auth_token(
            DBHostname=self._endpoint,
            Port=self._port,
            DBUsername=self._user,
            Region=self._region,
        )
        connection_string = f"postgresql+psycopg://{self._user}:{token}@{self._endpoint}:{self._port}/{self._dbname}?sslmode=require&sslrootcert=SSLCERTIFICATE"

        return sqlalchemy.create_engine(connection_string)


connector = Connector()
