import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)

class Settings:
    PROJECT_NAME: str = "Aziz AI Super Digital Clone - Backend"
    API_PREFIX: str = "/api"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    DB_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(BASE_DIR / 'aziz_ai.db').as_posix()}"
    )

settings = Settings()
