# app/routers/chat.py

from fastapi import APIRouter
from app.services.chat_service import create_chat_reply

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/chat")
async def chat_endpoint(message: str, external_id: str):
    reply = await create_chat_reply(external_id, message)
    return {"reply": reply}
