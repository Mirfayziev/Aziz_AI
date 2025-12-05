class Settings:
    PROJECT_NAME: str = "Aziz AI Super Digital Clone – Backend"

    API_PREFIX: str = "/api"   # <-- Muhim

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # DB_URL - eski kodlar bilan mosligi uchun
    DB_URL: str = DATABASE_URL  

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    PROJECT_DIR: str = str(BASE_DIR)
    URL: str = os.getenv("GITPAGELINK", "")
