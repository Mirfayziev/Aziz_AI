from sqlalchemy.orm import Session

from ..schemas import ProfileRequest


def update_profile(db: Session, payload: ProfileRequest) -> UserProfile:
    user = (
        db.query(UserProfile)
        .filter(UserProfile.external_id == payload.user_id)
        .first()
    )
    if not user:
        user = UserProfile(external_id=payload.user_id)
        db.add(user)

    if payload.name is not None:
        user.name = payload.name
    if payload.language is not None:
        user.language = payload.language

    db.commit()
    db.refresh(user)
    return user
