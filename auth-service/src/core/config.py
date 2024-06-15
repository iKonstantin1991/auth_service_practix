from logging import config as logging_config

from pydantic_settings import BaseSettings, SettingsConfigDict

from core.logger import LOGGING

logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    project_name: str = 'Auth API'

    postgres_db: str = 'postgres'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_host: str = '127.0.0.1'
    postgres_port: int = 5432

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    private_key: bytes
    public_key: bytes

    yandex_client_id: str
    yandex_client_secret: str

    echo_in_db: bool = True


settings = Settings()
