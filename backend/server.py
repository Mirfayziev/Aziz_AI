import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import chat, audio, memory, planner, summary, users, auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat")
app.include_router(audio.router, prefix="/audio")
app.include_router(memory.router, prefix="/memory")
app.include_router(planner.router, prefix="/planner")
app.include_router(summary.router, prefix="/summary")
app.include_router(users.router, prefix="/users")
app.include_router(auth.router, prefix="/auth")

@app.get("/")
def root():
    return {"msg": "Backend ishlayapti"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
