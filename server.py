import uvicorn
from fastapi import FastAPI, Request
from backend.app.main import app as backend_app

# Telegram bot funksiyasi
from telegram_bot.bot import process_update

app = FastAPI()

# Backend routerlarini FastAPI ga ulash
app.mount("/api", backend_app)

@app.get("/")
def home():
    return {"status": "Aziz AI backend + bot is running ✔️"}

# Telegram webhook endpoint (MUHIM!)
@app.post("/webhook")
async def telegram_webhook(request: Request):
    try:
        data = await request.json()
        await process_update(data)  # bot.py ichidagi handler
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
