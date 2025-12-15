from fastapi import FastAPI
from pydantic import BaseModel
from app.services.assistant_service import brain_query

app = FastAPI()

class AssistantRequest(BaseModel):
    user_id: str
    text: str
    voice: bool = False

class AssistantResponse(BaseModel):
    text: str
    audio_base64: str | None = None

@app.post("/assistant-message", response_model=AssistantResponse)
async def assistant_message(req: AssistantRequest):
    result = await brain_query(
        user_id=req.user_id,
        text=req.text,
        need_audio=req.voice
    )
    return result
