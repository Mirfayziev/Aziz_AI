from fastapi import APIRouter
from pydantic import BaseModel
import os
import httpx

router = APIRouter(tags=["chat"])

OPENAI_MODEL = os.getenv("MODEL_DEFAULT", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not OPENAI_API_KEY:
        return ChatResponse(reply="⚠️ OpenAI API key topilmadi")

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            res = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": OPENAI_MODEL,
                    "messages": [{"role": "user", "content": req.message}]
                }
            )

        data = res.json()
        reply = data["choices"][0]["message"]["content"]
        return ChatResponse(reply=reply)

    except Exception as e:
        return ChatResponse(reply=f"⚠️ AI backend xatosi: {e}")
