from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import chat, audio, planner, memory

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Backend")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(chat.router, prefix="/api/chat")
app.include_router(audio.router, prefix="/api/audio")
app.include_router(planner.router, prefix="/api/planner")
app.include_router(memory.router, prefix="/api/memory")


# Health check
@app.get("/")
def root():
    return {"message": "Aziz AI backend working ✔️"}
