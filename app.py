from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import Base, engine
from core.personality import router as personality_router
from core.memory.router import router as memory_router
from core.chat import router as chat_router
from core.agent import router as agent_router
from core.office import router as office_router
from core.audio import router as audio_router
from core.planner.router import planner_router

def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        debug=settings.DEBUG
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api_prefix = settings.API_PREFIX

    app.include_router(personality_router, prefix=api_prefix)
    app.include_router(memory_router, prefix=settings.API_PREFIX)
    app.include_router(chat_router, prefix=api_prefix)
    app.include_router(agent_router, prefix=api_prefix)
    app.include_router(office_router, prefix=api_prefix)
    app.include_router(audio_router, prefix=api_prefix)
    app.include_router(planner_router, prefix=API_PREFIX)
   
    @app.get("/")   # 👈 bitta qatorda bo‘lishi shart!
    async def root():
        return {
            "message": "Aziz AI Super Digital Clone - 6 yadroli backend ishlayapti ✔️",
            "modules": [
                "Personality Engine",
                "Memory Engine",
                "Chat Engine (GPT-5.1)",
                "Internet Agent",
                "Office Agent",
                "Voice + Animation Engine"
            ],
            "api_prefix": api_prefix
        }


    return app


init_db()
app = create_app()
