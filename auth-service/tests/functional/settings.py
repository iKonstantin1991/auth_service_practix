from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    postgres_db: str = 'postgres'
    postgres_user: str = 'postgres'
    postgres_password: str = 'postgres'
    postgres_host: str = '127.0.0.1'
    postgres_port: int = 5432

    redis_host: str = '127.0.0.1'
    redis_port: int = 6379

    service_host: str = '127.0.0.1'
    service_port: int = 8000


test_settings = TestSettings()
