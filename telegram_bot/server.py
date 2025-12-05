# server.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from chat import router as chat_router
from audio import router as audio_router
from users import router as users_router
from planner import router as planner_router
from memory import router as memory_router
from summary import router as summary_router

app = FastAPI(title="Aziz AI Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(chat_router, prefix="/api/chat")
app.include_router(audio_router, prefix="/api/audio")
app.include_router(users_router, prefix="/api/users")
app.include_router(planner_router, prefix="/api/planner")
app.include_router(memory_router, prefix="/api/memory")
app.include_router(summary_router, prefix="/api/summary")


@app.get("/")
def root():
    return {"message": "Aziz AI backend working ✔️"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False
    )
