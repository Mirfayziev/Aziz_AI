from fastapi import APIRouter

context_router = APIRouter(
    prefix="/api/context",
    tags=["Context"]
)

@context_router.get("/ping")
async def ping():
    return {"status": "ok", "module": "context"}
