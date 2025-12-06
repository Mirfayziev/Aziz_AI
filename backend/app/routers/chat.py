from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import ChatRequest, ChatResponse
from ..services.chat_service import create_chat_reply

router = APIRouter(tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)):
    try:
        reply = create_chat_reply(
            db,
            external_id=req.user_external_id,
            message=req.message,
            model_tier=req.model_tier,
        )
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
