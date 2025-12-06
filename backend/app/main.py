from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.chat import router as chat_router
from .routers.audio import router as audio_router
from .routers.assistant import router as assistant_router
from .routers.planner import router as planner_router
from .routers.profile import router as profile_router

app = FastAPI(
    title="Aziz AI Backend",
    version="1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTER ROUTERS
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(audio_router, prefix="/api", tags=["audio"])
app.include_router(assistant_router, prefix="/api", tags=["assistant"])
app.include_router(planner_router, prefix="/api", tags=["planner"])
app.include_router(profile_router, prefix="/api", tags=["profile"])

@app.get("/")
def root():
    return {"message": "Backend running ✔️"}
