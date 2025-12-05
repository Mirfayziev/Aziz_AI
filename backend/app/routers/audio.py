from fastapi import APIRouter, Depends, UploadFile, Form
from sqlalchemy.orm import Session

from app.db import get_db
from ..services.audio_service import process_audio_message

router = APIRouter()


@router.post("/")
async def audio_endpoint(
    user_id: str = Form(...),
    file: UploadFile = Form(...),
    db: Session = Depends(get_db),
):
    reply, text = await process_audio_message(db=db, external_user_id=user_id, file=file)
    return {"text": text, "reply": reply}
