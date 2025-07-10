import boto3
import json
import sqlalchemy
import os


class Connector:
    _instance = None

    _region_name = "us-east-1"
    _user: str
    _endpoint: str
    _port: str
    _dbname: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.set_credentials(
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
        return cls._instance

    def set_credentials(
        self,
        aws_access_key_id: str,
        aws_secret_access_key: str,
    ):
        boto_kwargs = {
            "region_name": self._region_name,
            "aws_access_key_id": aws_access_key_id,
            "aws_secret_access_key": aws_secret_access_key,
        }

        self._rds = boto3.client("rds", **boto_kwargs)
        self._secrets_manager = boto3.client("secretsmanager", **boto_kwargs)

        secret_response = self._secrets_manager.get_secret_value(SecretId="psr-lakehouse-secrets")
        secret = json.loads(secret_response["SecretString"])
        self._user = secret["POSTGRES_USER"]
        self._endpoint = secret["POSTGRES_SERVER"]
        self._port = secret["POSTGRES_PORT"]
        self._dbname = secret["POSTGRES_DB"]

    def engine(self) -> sqlalchemy.Engine:
        token = self._rds.generate_db_auth_token(
            DBHostname=self._endpoint,
            Port=self._port,
            DBUsername=self._user,
            Region=self._region_name,
        )
        connection_string = f"postgresql+psycopg://{self._user}:{token}@{self._endpoint}:{self._port}/{self._dbname}?sslmode=require&sslrootcert=SSLCERTIFICATE"

        return sqlalchemy.create_engine(connection_string)


connector = Connector()
