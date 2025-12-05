
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import chat, audio, planner

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])
app.include_router(planner.router, prefix="/api/planner", tags=["planner"])


@app.get("/")
def root():
    return {"message": "Aziz AI backend working"}
