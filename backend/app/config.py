from pydantic_settings import BaseSettings
from functools import lru_cache

import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
CURRENCY_API_KEY = os.getenv("CURRENCY_API_KEY", "")

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    DATABASE_URL: str = "sqlite:///./aziz_ai.db"

    MODEL_FAST: str = "gpt-4o-mini"
    MODEL_DEFAULT: str = "gpt-4o"
    MODEL_DEEP: str = "o1-mini"

    EMBEDDING_MODEL: str = "text-embedding-3-small"

    class Config:
        env_file = ".env"
        extra = "ignore"

@lru_cache
def get_settings() -> Settings:
    return Settings()
