"""Application Configuration"""

from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Database
    database_url: str = "postgresql://user:password@db:5432/landplan_db"
    database_echo: bool = False

    # Redis
    redis_url: str = "redis://redis:6379/0"

    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production-min-32-chars"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    jwt_refresh_expiration_days: int = 30

    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    debug: bool = True

    # CORS
    cors_origins: List[str] = ["https://landplan.xteam.pro", "http://localhost:3000", "http://localhost:5173"]

    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    # APIs
    yandex_maps_api_key: Optional[str] = None
    external_api_timeout: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
