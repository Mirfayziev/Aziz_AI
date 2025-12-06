import uvicorn
from fastapi import FastAPI, Request

# AI backend import
from app.main import app as ai_app

# Telegram bot import
import telegram.bot as tg_bot

app = FastAPI(title="Aziz AI + Telegram Bot")

# 1) AI backend routerlarini birlashtiramiz
app.mount("/api", ai_app)

# 2) Telegram webhook endpointi
@app.post("/webhook")
async def telegram_webhook(request: Request):
    update = await request.json()

    message = update.get("message") or {}
    if "text" in message:
        await tg_bot.handle_text_message(message)
    elif "voice" in message:
        await tg_bot.handle_voice_message(message)

    return {"ok": True}


@app.get("/")
def root():
    return {"status": "Aziz AI + Telegram Bot Running ✔️"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
