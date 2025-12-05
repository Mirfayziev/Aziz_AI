from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat Engine (GPT-5.1)"])


@router.get("/status")
def chat_status():
    return {
        "engine": "Chat Engine (GPT-5.1)",
        "status": "ok",
        "detail": "Chat API uchun skeleton tayyor. Keyingi bosqichda real OpenAI/GPT-5.1 ulanishi va streaming qo'shiladi."
    }
