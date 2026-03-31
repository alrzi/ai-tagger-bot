"""Конфигурация приложения. Загружается из переменных окружения."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram
    bot_token: str

    # PostgreSQL
    postgres_user: str = "ai_tagger"
    postgres_password: str = "secret_password"
    postgres_db: str = "ai_tagger"
    database_url: str = "postgresql+asyncpg://ai_tagger:secret_password@postgres:5432/ai_tagger"

    # Ollama
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "llama3"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
