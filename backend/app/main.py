from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .routers import tts

from .db import get_db
from .services.assistant_service import brain_query
from .schemas import BrainQueryRequest, BrainQueryResponse

app = FastAPI(title="Aziz AI Backend")

app.include_router(tts.router)
                   
@app.get("/")
def health():
    return {"status": "ok"}

# 🔥 TELEGRAM SHU YERGA KELADI
@app.post("/assistant-message", response_model=BrainQueryResponse)
def assistant_message(req: BrainQueryRequest, db: Session = Depends(get_db)):
    return brain_query(db, req)
