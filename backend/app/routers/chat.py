from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import create_chat_reply

router = APIRouter()

class ChatRequest(BaseModel):
    user_external_id: str
    message: str
    model_tier: str = "default"

class ChatResponse(BaseModel):
    reply: str

@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = create_chat_reply(req.message, req.model_tier)
    return ChatResponse(reply=reply)
