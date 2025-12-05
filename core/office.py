from fastapi import APIRouter

router = APIRouter(prefix="/office", tags=["Office Agent"])


@router.get("/status")
def office_status():
    return {
        "engine": "Office Agent",
        "status": "ok",
        "detail": "Word / Excel / PowerPoint avtomatlashtirish uchun API skeleton. Keyin python-docx, openpyxl va pptx qo'shiladi."
    }
