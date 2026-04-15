from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = Field(
        default="postgresql://user:password@localhost:5432/incidentes_db"
    )
    POSTGRES_USER: str = Field(default="user")
    POSTGRES_PASSWORD: str = Field(default="password")
    POSTGRES_DB: str = Field(default="incidentes_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)

    SECRET_KEY: str = Field(default="changeme-secret-key-min-32-chars!!")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    API_KEY_EXTERNAL: str = Field(default="changeme-external-api-key")
    EXTERNAL_API_URL: str = Field(default="http://external-api:8000")

    H3_RESOLUTION: int = Field(default=8)
    LOG_LEVEL: str = Field(default="INFO")

    CORS_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8501")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
