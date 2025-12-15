from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from openai import OpenAI
import io, os

router = APIRouter()
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

@router.post("/api/tts")
def tts(data: dict):
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=data["text"]
    )

    return StreamingResponse(
        io.BytesIO(speech.read()),
        media_type="audio/ogg"
    )
