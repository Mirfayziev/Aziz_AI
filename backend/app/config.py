import os
from functools import lru_cache
from openai import OpenAI


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "").strip()  # agar kerak bo'lsa

    MODEL_DEFAULT: str = os.getenv("MODEL_DEFAULT", "gpt-4.1-mini")
    MODEL_DEEP: str = os.getenv("MODEL_DEEP", "o1-mini")
    MODEL_FAST: str = os.getenv("MODEL_FAST", "gpt-4.1-mini")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")

    # audio
    TRANSCRIBE_MODEL: str = os.getenv("TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")
    TTS_MODEL: str = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_openai_client() -> OpenAI:
    settings = get_settings()
    if settings.OPENAI_BASE_URL:
        return OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    return OpenAI(api_key=settings.OPENAI_API_KEY)
