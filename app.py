from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.database import create_db_and_tables

# ROUTERS (13 modul uchun)
from core.memory.router import router as memory_router
from core.personality.router import router as personality_router
from core.profiling.router import router as profiling_router
from core.chat.router import router as chat_router
from core.context.router import router as context_router
from core.longterm.router import router as longterm_router
from core.shortterm.router import router as short_router
from core.office.router import router as office_router
from core.audio.router import router as audio_router
from core.agent.router import router as agent_router
from core.home.router import router as home_router
from core.mobile.router import router as mobile_router
from core.system.router import router as system_router


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Aziz AI – 13 module AI Backend (Memory, Profiling, Chat, Office, Voice, Agents)"
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routerlarni ulash
    app.include_router(memory_router,     prefix=settings.API_PREFIX)
    app.include_router(personality_router, prefix=settings.API_PREFIX)
    app.include_router(profiling_router,  prefix=settings.API_PREFIX)
    app.include_router(chat_router,       prefix=settings.API_PREFIX)
    app.include_router(context_router,    prefix=settings.API_PREFIX)
    app.include_router(longterm_router,   prefix=settings.API_PREFIX)
    app.include_router(short_router,      prefix=settings.API_PREFIX)
    app.include_router(office_router,     prefix=settings.API_PREFIX)
    app.include_router(audio_router,      prefix=settings.API_PREFIX)
    app.include_router(agent_router,      prefix=settings.API_PREFIX)
    app.include_router(home_router,       prefix=settings.API_PREFIX)
    app.include_router(mobile_router,     prefix=settings.API_PREFIX)
    app.include_router(system_router,     prefix=settings.API_PREFIX)

    @app.on_event("startup")
    async def startup_event():
        create_db_and_tables()

    @app.get("/")
    async def root():
        return {"message": "Aziz AI Backend 13-module super AI ishga tushdi ✔️"}

    return app


app = create_app()
