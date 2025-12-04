from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.models import MemoryEntry

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/{chat_id}", response_model=List[schemas.MemoryOut])
def list_memory(chat_id: str, db: Session = Depends(get_db)):
    entries = (
        db.query(MemoryEntry)
        .filter(MemoryEntry.chat_id == chat_id)
        .order_by(MemoryEntry.created_at.asc())
        .all()
    )
    return entries


@router.delete("/{chat_id}")
def clear_memory(chat_id: str, db: Session = Depends(get_db)):
    count = (
        db.query(MemoryEntry)
        .filter(MemoryEntry.chat_id == chat_id)
        .delete()
    )
    db.commit()
    if count == 0:
        raise HTTPException(status_code=404, detail="Hech qanday xotira topilmadi")
    return {"deleted": count}
