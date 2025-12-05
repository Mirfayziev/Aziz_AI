from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from . import schemas, service, models

router = APIRouter(
    prefix="/memory",
    tags=["Memory Engine"]
)

@router.post("/add", response_model=schemas.MemoryOut)
def add_mem(payload: schemas.MemoryAdd, db: Session = Depends(get_db)):
    mem = service.add_memory(db, payload)
    return mem

@router.post("/search", response_model=list[schemas.MemorySearchResult])
def search_mem(payload: schemas.MemorySearchRequest, db: Session = Depends(get_db)):
    return service.search_memory(db, payload.query, payload.top_k)

@router.get("/list", response_model=list[schemas.MemoryOut])
def list_memory(db: Session = Depends(get_db)):
    return service.list_memory(db)
