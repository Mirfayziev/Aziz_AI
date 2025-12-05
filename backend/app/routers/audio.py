from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import AudioRequest, AudioResponse
from app.services.audio_service import process_audio_message

router = APIRouter(tags=["audio"])


@router.post("", response_model=AudioResponse)
def handle_audio(req: AudioRequest, db: Session = Depends(get_db)):
    """
    Telegram botdan kelgan audio_base64 ni qabul qiladi,
    Whisper orqali matnga aylantiradi va chat modeli orqali javob qaytaradi.
    """
    try:
        text, reply = process_audio_message(
            db=db,
            external_id=req.user_external_id,
            audio_base64=req.audio_base64,
            model_tier=req.model_tier,
        )
        return AudioResponse(text=text, reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
