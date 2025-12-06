import uvicorn
from fastapi import FastAPI, Request

# AI Backend import (TO'G'RI YO'L)
from backend.app.main import app as ai_app

# Telegram bot import (TO'G'RI YO'L)
from telegram_bot.bot import handle_text_message, handle_voice_message

app = FastAPI(title="Aziz AI + Telegram Bot")

# 1) AI backend routerlarini /api tagiga mount qilamiz
app.mount("/api", ai_app)

# 2) Telegram WEBHOOK endpoini
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message") or {}

    if "text" in message:
        await handle_text_message(message)
    elif "voice" in message:
        await handle_voice_message(message)

    return {"ok": True}

# 3) Test endpoint
@app.get("/")
def root():
    return {"status": "Aziz AI + Telegram Bot Running ✔️"}

# 4) Run server
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
