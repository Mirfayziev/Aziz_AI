from fastapi import APIRouter
from .service import my_context_service   # ✔️ endi mavjud

context_router = APIRouter(prefix="/api/context")

@context_router.post("/add")
def add_context(data: dict):
    return my_context_service(data)
