from fastapi import APIRouter

router = APIRouter(prefix="/memory", tags=["Memory Engine"])


@router.get("/status")
def memory_status():
    return {
        "engine": "Memory Engine",
        "status": "ok",
        "detail": "Uzoq muddatli xotira uchun arxitektura tayyor. Keyingi bosqichda real storage (PostgreSQL + pgvector) qo'shiladi."
    }
