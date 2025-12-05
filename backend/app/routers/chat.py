
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.chat_service import create_chat_reply

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ChatRequest(BaseModel):
    user_id: str
    message: str
    full_name: str | None = None


class ChatResponse(BaseModel):
    reply: str


@router.post("", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    reply = create_chat_reply(
        db=db,
        external_user_id=payload.user_id,
        message=payload.message,
        full_name=payload.full_name,
    )
    return ChatResponse(reply=reply)
