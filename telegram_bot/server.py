from fastapi import FastAPI, Request, BackgroundTasks
import json
import bot  # bot.py dagi AI logika

app = FastAPI()

@app.get("/")
async def home():
    return {"status": "telegram bot server running"}

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):

    try:
        update = await request.json()
    except Exception:
        return {"ok": True}

    # bot.py ichidagi process_update funksiyasini backgroundda chaqiramiz
    background_tasks.add_task(bot.process_update, update)

    return {"ok": True}
