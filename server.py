from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routers
from backend.app.chat import router as chat_router
from backend.app.audio import router as audio_router
from backend.app.profile import router as profile_router
from backend.app.planner import router as planner_router

app = FastAPI(title="Aziz AI Backend")

# CORS (Telegram + browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend working ✔️"}

# === IMPORTANT ===
# Chat → /api/chat
# Audio → /api/audio
# Planner → /api/planner
# Profile → /api/profile
# =================
app.include_router(chat_router, prefix="/api/chat")
app.include_router(audio_router, prefix="/api/audio")
app.include_router(profile_router, prefix="/api/profile")
app.include_router(planner_router, prefix="/api/planner")


# Telegram webhook endpoint
@app.post("/webhook")
async def telegram_webhook(request: dict):
    from telegram_bot.bot import process_update
    return await process_update(request)
