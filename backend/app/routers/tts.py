from fastapi import APIRouter
import httpx
import os

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("/")
async def text_to_speech(text: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers=headers,
            json=payload
        )

    return {
        "audio": r.content.hex()  # telegramga yuborish uchun hex bo‘lib qaytadi
    }
