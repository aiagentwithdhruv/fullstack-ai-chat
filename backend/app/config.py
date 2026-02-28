from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "fullstack_ai_chat"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # App
    app_name: str = "Conversa AI"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # File Upload
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = [
        "pdf", "docx", "xlsx", "png", "jpg", "jpeg", "webp"
    ]

    # Rate Limiting
    rate_limit_per_minute: int = 20
    daily_token_budget: int = 100000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
