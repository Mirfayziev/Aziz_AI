from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routers.chat import router as chat_router
from .routers.audio import router as audio_router
from .routers.profile import router as profile_router
from .routers.planner import router as planner_router

# Agar kerak bo'lsa – tabelarni yaratish
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Pro Backend (6-core)")

# CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ⚠️ DIQQAT: bu yerda /api YO‘Q!
# Tashqi app allaqachon /api ga mount qilingan.
# Shuning uchun ichkarida faqat /chat, /audio va hokazo bo‘ladi.
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(audio_router, prefix="/audio", tags=["audio"])
app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(planner_router, prefix="/planner", tags=["planner"])

@app.get("/")
def root():
    return {"message": "Aziz AI Pro backend (6-core) working ✔️"}
