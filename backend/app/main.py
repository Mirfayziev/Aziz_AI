from fastapi import FastAPI
from pydantic import BaseModel
from app.services.assistant_service import brain_query

app = FastAPI()


class AssistantMessage(BaseModel):
    text: str
    user_id: str | None = "telegram"
    source: str | None = "telegram"


@app.post("/assistant-message")
async def assistant_message(payload: AssistantMessage):
    """
    Telegram / Web / APK dan kelgan xabarlarni qabul qiladi
    """
    answer = await brain_query(
        text=payload.text,
        user_id=payload.user_id,
        source=payload.source,
    )

    return {
        "text": answer
    }


@app.get("/")
def health():
    return {"status": "ok"}
