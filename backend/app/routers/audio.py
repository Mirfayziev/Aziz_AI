from fastapi import APIRouter, UploadFile, File
import httpx
import os

router = APIRouter(tags=["audio"])

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@router.post("", summary="Transcribe Audio")      # ✅ /api/audio
@router.post("/", summary="Transcribe Audio")     # ✅ /api/audio/
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            audio_bytes = await file.read()

            files = {
                "file": (file.filename, audio_bytes, file.content_type)
            }

            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}"
            }

            data = {
                "model": "gpt-4o-transcribe"   # ✅ TO‘G‘RI MODEL (Speech → Text)
            }

            res = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data
            )

            result = res.json()

            return {
                "text": result.get("text", "")
            }

    except Exception as e:
        return {
            "error": f"⚠️ Audio backend xatosi: {e}"
        }
