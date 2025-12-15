from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.services.chat_service import create_chat_reply

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    external_id: str
    message: str

@router.post("/chat")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    reply = create_chat_reply(db, req.external_id, req.message)
    return {"reply": reply}
