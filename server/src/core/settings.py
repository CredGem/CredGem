from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "CredGem API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # Server Configuration
    PORT: str = "8000"
    RELOAD: bool = False
    ENV: Literal["dev", "prod", "test"] = "dev"

    # Database Configuration
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    DB_NAME: str = "credgem"
    TEST_DB_NAME: str = "credgem_test"

    # CORS Configuration
    CORS_ALLOWED_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # Logging Configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @property
    def ASYNC_DATABASE_URL(self) -> str:
        db_name = self.DB_NAME if not self.ENV == "test" else self.TEST_DB_NAME
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{db_name}"
        )

    @property
    def CORS_ALLOWED_ORIGINS_LIST(self) -> list[str]:
        return to_list(self.CORS_ALLOWED_ORIGINS)

    @property
    def CORS_ALLOWED_METHODS_LIST(self) -> list[str]:
        return to_list(self.CORS_ALLOW_METHODS)

    @property
    def CORS_ALLOWED_HEADERS_LIST(self) -> list[str]:
        return to_list(self.CORS_ALLOW_HEADERS)

    # Pydantic Configuration
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


def to_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


settings = Settings()
