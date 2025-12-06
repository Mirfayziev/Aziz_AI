from fastapi import FastAPI
from .routers.chat import router as chat_router
from .routers.audio import router as audio_router
from .routers.profile import router as profile_router
from .routers.planner import router as planner_router

app = FastAPI() 

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Aziz AI Pro Backend (6-core)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")
app.include_router(audio_router, prefix="/api")
app.include_router(profile_router, prefix="/api")
app.include_router(planner_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Aziz AI Pro backend (6-core) working ✔️"}
