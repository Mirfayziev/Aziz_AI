
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.audio_service import process_audio

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
async def audio_endpoint(
    user_id: str = Form(...),
    full_name: str | None = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        data = await file.read()
        result = process_audio(db, external_user_id=user_id, audio_bytes=data, full_name=full_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
