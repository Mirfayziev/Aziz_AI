from fastapi import APIRouter

chat_router = APIRouter(
    prefix="/api/chat",
    tags=["Chat"],
)

@chat_router.get("/ping")
async def ping():
    return {"status": "ok", "module": "chat"}
