from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import ProfileUpdate, Profile
from app.services.profile_service import update_profile

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/", response_model=Profile)
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
