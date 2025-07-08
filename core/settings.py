from datetime import timedelta
from logging import config as logging_config

from async_fastapi_jwt_auth import AuthJWT
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings

from core.logger import LOGGING


# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class PostgresSettings(BaseSettings):
    """Postgres settings."""

    echo_database: bool = False
    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    @property
    def pg_dsn(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )


class Settings(PostgresSettings):
    # Общие настройки
    project_name: str = "Auth"
    debug: bool = False

    # Настройки Redis
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379

    # Настройки AuthJWT
    authjwt_secret_key: str = "secret"
    authjwt_access_token_expires: timedelta = timedelta(minutes=15)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)

    # Настройки Google Auth
    google_redirect_uri: str = "http://localhost:8000/google/auth"
    google_client_id: str = "***.apps.googleusercontent.com"
    google_client_secret: str = "***"

    # Настройка телеметрии
    jaeger_trace: bool = True
    jaeger_agent_host: str = "localhost"
    jaeger_agent_port: int = 6831

    # Настройки лимитирования запросов
    request_limit: int = 20

    @property
    def google_client_config(self):
        return {
            "web": {
                "client_id": self.google_client_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": self.google_client_secret,
                "redirect_uris": [self.google_redirect_uri],
                "javascript_origins": [],
            }
        }


@AuthJWT.load_config
def get_config():
    return Settings()


settings = Settings()
