from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ChatRequest, ChatResponse
from ..services.chat_service import create_chat_reply

router = APIRouter()


@router.post("/", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db)):
    reply, used_model = create_chat_reply(
        db=db,
        external_user_id=payload.user_id,
        message=payload.message,
        model_tier=payload.model_tier,
    )
    return ChatResponse(reply=reply, used_model=used_model)
