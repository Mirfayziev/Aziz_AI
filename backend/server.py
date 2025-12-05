from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat import router as chat_router
from audio import router as audio_router
from auth import router as auth_router
from planner import router as planner_router
from summary import router as summary_router
from users import router as users_router

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
app.include_router(chat_router, prefix="/api/chat")
app.include_router(audio_router, prefix="/api/audio")
app.include_router(auth_router, prefix="/api/auth")
app.include_router(planner_router, prefix="/api/planner")
app.include_router(summary_router, prefix="/api/summary")
app.include_router(users_router, prefix="/api/users")

@app.get("/")
async def root():
    return {"message": "Backend working ✔️"}
