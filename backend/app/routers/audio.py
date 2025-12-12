# backend/app/routers/audio.py

import os
import httpx
from fastapi import APIRouter, UploadFile, File

router = APIRouter(tags=["audio"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
TRANSCRIBE_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe").strip()


@router.post("", summary="Transcribe Audio")      # /api/audio
@router.post("/", summary="Transcribe Audio")     # /api/audio/
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        if not OPENAI_API_KEY:
            return {"error": "OPENAI_API_KEY is not set"}

        audio_bytes = await file.read()

        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        data = {"model": TRANSCRIBE_MODEL}

        files = {"file": (file.filename or "audio.ogg", audio_bytes, file.content_type or "audio/ogg")}

        async with httpx.AsyncClient(timeout=180) as client:
            res = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
            )

        if res.status_code >= 400:
            return {"error": f"⚠️ Audio transcribe failed: {res.status_code} {res.text}"}

        result = res.json()
        return {"text": (result.get("text") or "").strip()}

    except Exception as e:
        return {"error": f"⚠️ Audio backend xatosi: {e}"}
