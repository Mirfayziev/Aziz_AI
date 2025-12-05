from core.memory.router import router as memory_router
app.include_router(memory_router, prefix="/api")
