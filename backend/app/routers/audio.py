from fastapi import APIRouter, UploadFile, File
from openai import OpenAI
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@router.post("/audio")
async def audio_to_text(file: UploadFile = File(...)):
    try:
        content = await file.read()

        result = client.audio.transcriptions.create(
            model="gpt-4o-mini-tts",  # Agar whisper kerak bo'lsa: "whisper-1"
            file=("audio.ogg", content)
        )

        return {"text": result.text}

    except Exception as e:
        return {"error": str(e)}
