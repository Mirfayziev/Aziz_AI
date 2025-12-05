import os
import uvicorn
from fastapi import FastAPI, Request
from bot import bot, process_update  # bot.py dagi obyektlar

app = FastAPI(title="Aziz AI Telegram Bot")

# Telegram webhook yo'li
WEBHOOK_PATH = "/webhook"

# Railway domeningga mos URL
DEFAULT_WEBHOOK_BASE = "https://focused-benevolence-production.up.railway.app"
WEBHOOK_URL = os.getenv("WEBHOOK_URL", DEFAULT_WEBHOOK_BASE + WEBHOOK_PATH)


@app.on_event("startup")
async def on_startup():
    # Bot ishga tushganda webhook'ni o'rnatamiz
    await bot.set_webhook(WEBHOOK_URL)


@app.on_event("shutdown")
async def on_shutdown():
    # Servis to'xtaganda webhookni o'chiramiz
    await bot.delete_webhook()


@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    """
    Telegramdan kelgan barcha update shu endpointga keladi.
    """
    update_json = await request.json()
    await process_update(update_json)
    return {"ok": True}


@app.get("/")
async def healthcheck():
    return {"status": "ok", "service": "telegram-bot"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    # Bu yerda uvicorn'ni o'zimiz ishga tushiramiz – $PORT bilan muammo bo‘lmaydi
    uvicorn.run("server:app", host="0.0.0.0", port=port)
