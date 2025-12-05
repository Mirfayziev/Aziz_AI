from fastapi import APIRouter

router = APIRouter(prefix="/agent", tags=["Internet Agent"])


@router.get("/status")
def agent_status():
    return {
        "engine": "Internet Agent",
        "status": "ok",
        "detail": "Telegram / Instagram agentlari uchun API skeleton tayyor. Keyingi bosqichda webhook va auto-reply logic qo'shiladi."
    }
