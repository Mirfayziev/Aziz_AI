from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.personality.service import (
    get_profile,
    create_profile,
    delete_profile
)

router = APIRouter(prefix="/api/personality", tags=["Personality Engine"])

@router.get("/{profile_id}")
def get_personality(profile_id: str, db: Session = Depends(get_db)):
    return get_profile(db, profile_id)

@router.post("/")
def create_personality(data: dict, db: Session = Depends(get_db)):
    traits = data.get("traits", {})
    preferences = data.get("preferences", {})
    return create_profile(db, traits, preferences)

@router.delete("/{profile_id}")
def delete_personality(profile_id: str, db: Session = Depends(get_db)):
    return delete_profile(db, profile_id)
