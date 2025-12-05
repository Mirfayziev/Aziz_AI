from fastapi import APIRouter

router = APIRouter(prefix="/voice", tags=["Voice + Animation Engine"])


@router.get("/status")
def voice_status():
    return {
        "engine": "Voice + Animation Engine",
        "status": "ok",
        "detail": "Ovoz va animatsiya uchun backend skeleton tayyor. Keyingi bosqichda TTS va avatar integratsiyasi qo'shiladi."
    }
