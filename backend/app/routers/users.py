from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas, models
from app.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=schemas.UserOut)
def update_me(
    payload: schemas.ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.bio is not None:
        current_user.bio = payload.bio
    if payload.goals is not None:
        current_user.goals = payload.goals
    if payload.interests is not None:
        current_user.interests = payload.interests
    if payload.personality is not None:
        current_user.personality = payload.personality
    if payload.timezone is not None:
        current_user.timezone = payload.timezone

    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user
