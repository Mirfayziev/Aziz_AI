from fastapi import APIRouter
import httpx
import os

router = APIRouter()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@router.post("")
async def text_to_speech(payload: dict):
    text = payload.get("text")

    if not text:
        return {"error": "text not provided"}

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini-tts",
        "voice": "alloy",
        "input": text
    }

    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers=headers,
            json=data
        )

    return {
        "audio_base64": r.content.hex()
    }
