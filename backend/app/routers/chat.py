# app/routers/chat.py

from fastapi import APIRouter
from pydantic import BaseModel
from app.services.chat_service import create_chat_reply
from app.db import get_user_context, save_user_message, save_ai_message

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    external_id: str
    message: str

@router.post("/chat")
async def chat_endpoint(payload: ChatRequest):
    user_id = payload.external_id
    user_message = payload.message

    # 1) Foydalanuvchi kontekstini olish
    context = get_user_context(user_id)

    # 2) Foydalanuvchi xabarini DB ga saqlash
    save_user_message(user_id, user_message)

    # 3) AI javobini yaratish
    ai_reply = await create_chat_reply(user_message, context)

    # 4) AI javobini saqlash
    save_ai_message(user_id, ai_reply)

    return {"reply": ai_reply}
