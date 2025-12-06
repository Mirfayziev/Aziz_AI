from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Routerlarni import qilish (SENING TUZILMANG BO‘YICHA)
from backend.app.routers.chat import router as chat_router
from backend.app.routers.audio import router as audio_router
from backend.app.routers.assistant import router as assistant_router
from backend.app.routers.planner import router as planner_router
from backend.app.routers.profile import router as profile_router

app = FastAPI(title="Aziz AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(audio_router, prefix="/api/audio", tags=["audio"])
app.include_router(assistant_router, prefix="/api/assistant", tags=["assistant"])
app.include_router(planner_router, prefix="/api/planner", tags=["planner"])
app.include_router(profile_router, prefix="/api/profile", tags=["profile"])

@app.get("/")
def root():
    return {"message": "Backend running"}
