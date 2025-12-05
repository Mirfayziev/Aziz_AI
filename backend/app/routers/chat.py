from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import create_chat_reply

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

# BU joyni to‘g‘irladik — endpoint endi POST /api/chat
@router.post("")
async def chat_reply(payload: ChatRequest):
    reply = await create_chat_reply(
        user_id=payload.user_id,
        message=payload.message
    )
    return {"reply": reply}
