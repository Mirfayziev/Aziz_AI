from fastapi import APIRouter
from app.services.chat import chat_service

router = APIRouter()

MODEL_URL = os.getenv("MODEL_DEEP")

@router.post("/")
async def chat_endpoint(payload: dict):
    """
    Telegram bot backend → Chat model → javob qaytaradi
    """
    try:
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(MODEL_URL, json=payload)

        return response.json()

    except Exception as e:
        return {"error": str(e)}
