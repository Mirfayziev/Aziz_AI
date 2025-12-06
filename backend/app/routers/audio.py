from fastapi import APIRouter, UploadFile
import httpx
import os

router = APIRouter(tags=["audio"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@router.post("/")
async def transcribe_audio(file: UploadFile):
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            files = {"file": (file.filename, await file.read(), file.content_type)}

            res = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                files=files,
                data={"model": "gpt-4o-mini-tts"}
            )

        return {"text": res.json().get("text", "")}

    except Exception as e:
        return {"error": f"⚠️ Audio backend xatosi: {e}"}
