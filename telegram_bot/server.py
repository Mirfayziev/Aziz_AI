from fastapi import FastAPI, Request
import uvicorn
import json
from bot import handle_update  # botdagi asosiy handler

app = FastAPI()

@app.post("/")
async def webhook(request: Request):
    update = await request.json()
    handle_update(update)
    return {"ok": True}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8001)
