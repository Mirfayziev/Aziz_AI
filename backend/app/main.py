from fastapi import FastAPI, Request
from app.services.assistant_service import brain_query

app = FastAPI()

@app.post("/assistant-message")
async def assistant_message(request: Request):
    data = await request.json()
    text = data.get("text", "")

    answer, audio_bytes = await brain_query(text)

    return {
        "text": answer,
        "audio": audio_bytes.hex()
    }
