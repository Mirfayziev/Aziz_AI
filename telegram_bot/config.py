import os
from dotenv import load_dotenv

load_dotenv()  # agar .env bo'lsa, o'qib oladi

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

BACKEND_CHAT_URL = os.getenv("BACKEND_CHAT_URL", "")
BACKEND_AUDIO_URL = os.getenv("BACKEND_AUDIO_URL", "")
BACKEND_PLANNER_URL = os.getenv("BACKEND_PLANNER_URL", "")

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN environment o'rnatilmagan")

if not BACKEND_CHAT_URL:
    raise RuntimeError("BACKEND_CHAT_URL environment o'rnatilmagan")

if not BACKEND_AUDIO_URL:
    raise RuntimeError("BACKEND_AUDIO_URL environment o'rnatilmagan")

if not BACKEND_PLANNER_URL:
    raise RuntimeError("BACKEND_PLANNER_URL environment o'rnatilmagan")
