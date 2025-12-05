from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import create_chat_reply

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

@router.post("/")
def chat_endpoint(payload: ChatRequest):
    reply = create_chat_reply(payload.user_id, payload.message)
    return {"reply": reply}
