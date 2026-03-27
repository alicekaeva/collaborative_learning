from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Collaborative Learning API"
    API_V1_STR: str = "/api/v1"

    # No default — app will fail at startup if SECRET_KEY is missing from .env
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "cluser"
    # No default — app will fail at startup if POSTGRES_PASSWORD is missing from .env
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "collaborative_learning"

    # No default — app will fail at startup if REDIS_URL is missing from .env
    REDIS_URL: str

    UPLOAD_DIR: str = "/app/uploads/materials"
    MAX_FILE_SIZE_MB: int = 50

    # Safe default: explicit origins only. Wildcard forbidden with credentials.
    ALLOWED_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]

    # Set to True in production (requires HTTPS)
    COOKIE_SECURE: bool = False

    RECOMMENDATIONS_CACHE_TTL: int = 300  # 5 minutes

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def MAX_FILE_SIZE(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024


settings = Settings()
