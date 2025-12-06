from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db import get_db
from ..schemas import ProfileUpdate, Profile
from ..services.profile_service import update_profile
from ..services.memory_service import get_or_create_user

router = APIRouter(tags=["profile"])

@router.post("/update", response_model=Profile)
def update_profile_endpoint(req: ProfileUpdate, db: Session = Depends(get_db)):
    user = update_profile(
        db,
        external_id=req.user_external_id,
        name=req.name,
        bio=req.bio,
        goals=req.goals,
        interests=req.interests,
    )
    return Profile(
        user_external_id=user.external_id,
        name=user.name,
        bio=user.bio,
        goals=user.goals,
        interests=user.interests,
    )

@router.get("/{external_id}", response_model=Profile)
def get_profile(external_id: str, db: Session = Depends(get_db)):
    user = get_or_create_user(db, external_id)
    return Profile(
        user_external_id=user.external_id,
        name=user.name,
        bio=user.bio,
        goals=user.goals,
        interests=user.interests,
    )
