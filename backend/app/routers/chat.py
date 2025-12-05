from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import create_chat_reply

router = APIRouter()

class ChatRequest(BaseModel):
    user_id: int
    message: str

@router.post("")   # /api/chat
async def chat_reply(payload: ChatRequest):
    reply = await create_chat_reply(
        user_id=payload.user_id,
        message=payload.message
    )
    return {"reply": reply}
