from sqlalchemy.orm import Session
from ..models import User
from app.db import get_or_create_user

def update_profile(
    db: Session,
    external_id: str,
    name: str | None = None,
    bio: str | None = None,
    goals: list[str] | None = None,
    interests: list[str] | None = None,
) -> User:
    from .memory_service import get_or_create_user
    user = get_or_create_user(db, external_id)

    if name is not None:
        user.name = name
    if bio is not None:
        user.bio = bio
    if goals is not None:
        user.goals = goals
    if interests is not None:
        user.interests = interests

    db.add(user)
    db.commit()
    db.refresh(user)
    return user

