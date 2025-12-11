# app/routers/chat.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chat_service import create_chat_reply

router = APIRouter()


@router.post("/chat")
def chat_endpoint(
    message: str,
    external_id: str,
    db: Session = Depends(get_db)
):
    reply = create_chat_reply(db, external_id, message)
    return {"reply": reply}
