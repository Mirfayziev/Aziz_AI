from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers.chat import router as chat_router
from .routers.audio import router as audio_router
from .routers.profile import router as profile_router
from .routers.planner import router as planner_router

# ❗ App faqat 1 martta yaratiladi
app = FastAPI(title="Aziz AI Pro Backend (6-core)")

# ❗ Database yaratish
Base.metadata.create_all(bind=engine)

# ❗ CORS sozlamalari
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ❗ Routerlarni to‘g‘ri ulash
app.include_router(chat_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(planner_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Aziz AI Pro backend (6-core) working ✔️"}
