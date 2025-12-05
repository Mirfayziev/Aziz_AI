import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(ENV_PATH)

class Settings:
    PROJECT_NAME: str = "Aziz AI Super Digital Clone – Backend"

    API_PREFIX: str = "/api"   # ✅ MUHIM QO‘SHILGAN QATOR

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    PROJECT_DIR: str = str(BASE_DIR)
    URL: str = os.getenv("GITPAGELINK", "")

settings = Settings()
