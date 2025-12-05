from fastapi import APIRouter
from core.profiling.service import get_events, add_event

profiling_router = APIRouter(prefix="/api/profiling", tags=["Profiling"])

@profiling_router.get("/")
def list_events():
    return get_events()

@profiling_router.post("/")
def create_event(data: dict):
    return add_event(data)
