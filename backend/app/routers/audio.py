from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.audio_service import process_audio

router = APIRouter()


class AudioRequest(BaseModel):
    user_id: int
    audio_base64: str


@router.post("/")
def audio_endpoint(payload: AudioRequest, db: Session = Depends(get_db)):
    try:
        result = process_audio(
            db=db,
            user_id=payload.user_id,
            audio_base64=payload.audio_base64
        )
        return result  # {"text": "...", "reply": "..."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
