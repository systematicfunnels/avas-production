from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_ENV: str = "production"
    APP_SECRET_KEY: str
    APP_DEBUG: bool = False
    APP_NAME: str = "AVAS"
    APP_VERSION: str = "1.0.0"
    APP_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # Object Storage
    MINIO_ENDPOINT: str
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_BUCKET_INSPECTIONS: str = "avas-inspections"
    MINIO_BUCKET_RESULTS: str = "avas-results"
    MINIO_USE_SSL: bool = False

    # AI Service
    AI_SERVICE_URL: str = "http://ai_service:8001"
    AI_INFERENCE_TIMEOUT: int = 120
    AI_MAX_IMAGE_SIZE_MB: int = 50
    AI_CONFIDENCE_THRESHOLD: float = 0.5

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"

    @field_validator("APP_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def max_image_bytes(self) -> int:
        return self.AI_MAX_IMAGE_SIZE_MB * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    return Settings()
