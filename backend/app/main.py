from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import chat, audio, planner, profile, assistant

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Pro Backend (6-core)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat")
app.include_router(audio.router, prefix="/api/audio")
app.include_router(planner.router, prefix="/api/planner")
app.include_router(profile.router, prefix="/api/profile")
app.include_router(assistant.router, prefix="/api/assistant")

@app.get("/")
def root():
    return {"message": "Aziz AI Pro backend (6-core) working ✔️"}
