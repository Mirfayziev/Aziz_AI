from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chat_service import create_chat_reply

router = APIRouter()


class ChatRequest(BaseModel):
    user_id: int
    message: str
    model_tier: str = "default"


@router.post("")
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    reply = create_chat_reply(
        db=db,
        user_id=payload.user_id,
        message=payload.message,
        model_tier=payload.model_tier,
    )
    return {"reply": reply}
