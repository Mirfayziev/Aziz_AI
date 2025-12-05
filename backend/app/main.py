from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import chat, audio, planner, profile
from app.routers import planner

# DB create
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Pro Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(chat.router, prefix="/api/chat")
app.include_router(audio.router, prefix="/api/audio")
app.include_router(planner.router, prefix="/api/planner")
app.include_router(profile.router, prefix="/api/profile")

# HEALTH CHECK
@app.get("/")
def root():
    return {"message": "Aziz AI Pro backend working ✔️"}
