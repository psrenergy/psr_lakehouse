import json
import boto3
import sqlalchemy


class Connector:
    _instance = None
    _user: str
    _endpoint: str
    _port: str
    _dbname: str
    
    _aws_access_key_id: str | None = None
    _aws_secret_access_key: str | None = None
    _aws_region_name: str

    @classmethod
    def set_credentials(
        cls,
        aws_access_key_id: str,
        aws_secret_access_key: str,
        aws_region_name: str = "us-east-1",
    ):
        cls._aws_access_key_id = aws_access_key_id
        cls._aws_secret_access_key = aws_secret_access_key
        cls._aws_region_name = aws_region_name
        cls._instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        boto3_kwargs = {"region_name": self._aws_region_name}
        if self._aws_access_key_id and self._aws_secret_access_key:
            boto3_kwargs["aws_access_key_id"] = self._aws_access_key_id
            boto3_kwargs["aws_secret_access_key"] = self._aws_secret_access_key

        self._rds = boto3.client("rds", **boto3_kwargs)
        self._secrets_manager = boto3.client("secretsmanager", **boto3_kwargs)

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
            Region=self._region,
        )
        connection_string = f"postgresql+psycopg://{self._user}:{token}@{self._endpoint}:{self._port}/{self._dbname}?sslmode=require&sslrootcert=SSLCERTIFICATE"

        return sqlalchemy.create_engine(connection_string)


connector = Connector()
