from fastapi import FastAPI

# To‘g‘ri importlar — routers papkasidan olish
from backend.app.routers.chat import router as chat_router
from backend.app.routers.audio import router as audio_router
from backend.app.routers.planner import router as planner_router
from backend.app.routers.profile import router as profile_router

app = FastAPI(title="Aziz AI Backend")

@app.get("/")
def root():
    return {"message": "Backend working ✔️"}

# Routerlarni ulash
app.include_router(chat_router, prefix="/api/chat")
app.include_router(audio_router, prefix="/api/audio")
app.include_router(planner_router, prefix="/api/planner")
app.include_router(profile_router, prefix="/api/profile")
