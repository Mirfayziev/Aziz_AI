import uvicorn
from fastapi import FastAPI, Request

# Import AI Backend
from app.main import app as ai_app

# Import Telegram Bot
from telegram_bot.bot import handle_text_message, handle_voice_message

app = FastAPI(title="Aziz AI Backend + Telegram Bot")

# ------------------------------------------------------
# 1) AI backend routerlarini mount qilamiz
# ------------------------------------------------------
app.mount("/api", ai_app)


# ------------------------------------------------------
# 2) Telegram WEBHOOK endpoint
# ------------------------------------------------------
@app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()

    message = update.get("message") or {}

    if "text" in message:
        await handle_text_message(message)
    elif "voice" in message:
        await handle_voice_message(message)

    return {"ok": True}


# ------------------------------------------------------
# 3) Root test
# ------------------------------------------------------
@app.get("/")
async def root():
    return {"status": "Aziz AI + Telegram Bot running ✔️"}


# ------------------------------------------------------
# 4) Main
# ------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
