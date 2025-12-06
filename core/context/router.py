from fastapi import APIRouter
from .service import my_context_service  # misol

router = APIRouter(prefix="/context", tags=["context"])

@router.get("/")
def get_context():
    return {"status": "ok"}
