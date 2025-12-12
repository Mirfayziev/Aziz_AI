# backend/app/routers/tts.py

import os
import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

router = APIRouter(tags=["tts"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TTS_MODEL = os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts").strip()
TTS_VOICE = os.getenv("OPENAI_TTS_VOICE", "alloy").strip()  # xohlasangiz o'zgartirasiz


@router.post("", summary="Text to Speech (returns ogg bytes)")
@router.post("/", summary="Text to Speech (returns ogg bytes)")
async def text_to_speech(payload: dict):
    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not set")

    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="text not provided")

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    data = {
        "model": TTS_MODEL,
        "voice": TTS_VOICE,
        "input": text,
        "format": "ogg_opus",
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            "https://api.openai.com/v1/audio/speech",
            headers=headers,
            json=data,
        )

    if r.status_code >= 400:
        raise HTTPException(status_code=500, detail=f"TTS failed: {r.status_code} {r.text}")

    # Return raw ogg bytes
    return Response(content=r.content, media_type="audio/ogg")
