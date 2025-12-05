# core/personality/router.py

from fastapi import APIRouter
from core.personality.service import apply_personality

router = APIRouter(prefix="/api/personality", tags=["Personality Engine"])

@router.post("/chat")
async def chat_with_personality(message: str):
    result = await apply_personality(message)
    return {"response": result}

@router.get("/profile")
async def get_profile():
    from core.personality.model import personality
    return personality.export()
