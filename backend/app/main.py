from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.chat import router as chat_router
from app.routers.audio import router as audio_router
from app.routers.assistant import router as assistant_router
from app.routers.planner import router as planner_router
from app.routers.profile import router as profile_router

app = FastAPI(title="Aziz AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])
app.include_router(audio_router, prefix="/api/audio", tags=["Audio"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["Assistant"])
app.include_router(planner_router, prefix="/api/planner", tags=["Planner"])
app.include_router(profile_router, prefix="/api/profile", tags=["Profile"])

@app.get("/")
async def root():
    return {"status": "Aziz AI backend is running ✔️"}
