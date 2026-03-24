from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Collaborative Learning API"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    POSTGRES_SERVER: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "cluser"
    POSTGRES_PASSWORD: str = "clpassword"
    POSTGRES_DB: str = "collaborative_learning"

    REDIS_URL: str = "redis://:redispassword@redis:6379/0"

    UPLOAD_DIR: str = "/app/uploads/materials"
    MAX_FILE_SIZE_MB: int = 50

    ALLOWED_ORIGINS: List[str] = ["*"]

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
