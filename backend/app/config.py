from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://refurbhub:refurbhub@localhost:5432/refurbhub"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    cors_origins: list[str] = ["http://localhost:3000"]

    scheduler_interval_minutes: int = 60
    scraper_rate_limit_per_second: float = 1.0
    scraper_max_retries: int = 3

    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    api_v1_prefix: str = "/api/v1"

    model_config = {"env_prefix": "REFURBHUB_"}


settings = Settings()
