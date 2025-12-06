from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    user_id: str | None = None

@router.post("/chat")
async def chat(req: ChatRequest):
    return {"reply": f"Siz yozdingiz: {req.message}"}
