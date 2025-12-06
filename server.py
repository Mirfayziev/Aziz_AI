import uvicorn
from fastapi import FastAPI, Request

# AI backend (TO'G'RI IMPORT YO'LI)
from backend.app.main import app as ai_app

# Telegram bot (TO'G'RI IMPORT YO'LI)
from telegram_bot.bot import handle_text_message, handle_voice_message

# Bitta umumiy FastAPI app yaratamiz
app = FastAPI(title="Aziz AI + Telegram Bot")

# 1) AI backend routerlarini mount qilamiz
app.mount("/api", ai_app)

# 2) Telegram webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    message = update.get("message") or {}

    if "text" in message:
        await handle_text_message(message)
    elif "voice" in message:
        await handle_voice_message(message)

    return {"ok": True}

# Test endpoint
@app.get("/")
async def root():
    return {"status": "Aziz AI + Telegram Bot Running ✔️"}

# Local run (Railway ham shuni ishlatadi)
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
