import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

class Settings:
    PROJECT_NAME: str = "Aziz AI — Super Digital Clone"
    API_PREFIX: str = "/api"

    DB_URL: str = os.getenv("DATABASE_URL", "")
    OPENAI_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

settings = Settings()
