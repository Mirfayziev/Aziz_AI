from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from openai import OpenAI
from ..config import get_settings
from ..db import get_db
from ..services.chat_service import create_chat_reply
from ..schemas import AudioChatResponse

router = APIRouter(tags=["audio"])
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        content = await file.read()
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, content)
        )
        return {"text": transcript.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=AudioChatResponse)
async def audio_chat(
    user_external_id: str = Form(...),
    model_tier: str = Form("default"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        content = await file.read()
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, content)
        )
        text = transcript.text
        reply = create_chat_reply(
            db,
            external_id=user_external_id,
            message=text,
            model_tier=model_tier,
        )
        return AudioChatResponse(text=text, reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
