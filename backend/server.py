from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.chat import router as chat_router
from routers.audio import router as audio_router
from routers.auth import router as auth_router
from routers.planner import router as planner_router
from routers.summary import router as summary_router
from routers.users import router as users_router

app = FastAPI(title="Aziz AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(chat_router, prefix="/chat")
app.include_router(audio_router, prefix="/audio")
app.include_router(auth_router, prefix="/auth")
app.include_router(planner_router, prefix="/planner")
app.include_router(summary_router, prefix="/summary")
app.include_router(users_router, prefix="/users")

@app.get("/")
def home():
    return {"msg": "Backend is working!"}
