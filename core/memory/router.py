# core/memory/router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.memory.service import add_memory, search_memory, delete_memory

router = APIRouter(prefix="/api/memory", tags=["Memory Engine"])

@router.post("/add")
async def add_memory_api(user_id: str, content: str, db: Session = Depends(get_db)):
    result = await add_memory(db, user_id, content)
    return {"status": "ok", "inserted": result.id}

@router.post("/search")
async def search_memory_api(query: str, db: Session = Depends(get_db)):
    result = await search_memory(db, query)
    return {"results": result}

@router.delete("/delete/{memory_id}")
async def delete_memory_api(memory_id: int, db: Session = Depends(get_db)):
    result = await delete_memory(db, memory_id)
    return {"deleted": result}
