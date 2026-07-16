from fastapi import APIRouter

from app.schemas import ChatRequest, ChatResponse
from app.services.chat_service import chat_with_ai

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    answer = await chat_with_ai(text=req.message, user_id=req.user_external_id)
    return ChatResponse(reply=answer)
