from fastapi import FastAPI, Request
from bot import handle_update

app = FastAPI()

@app.get("/")
def home():
    return {"status": "telegram bot running"}

@app.post("/")
async def webhook(request: Request):
    update = await request.json()
    await handle_update(update)
    return {"ok": True}
