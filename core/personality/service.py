from sqlalchemy.orm import Session
from core.personality.model import PersonalityProfile

def get_profile(db: Session, profile_id: str):
    return db.query(PersonalityProfile).filter(
        PersonalityProfile.id == profile_id
    ).first()

def create_profile(db: Session, traits: dict, preferences: dict):
    profile = PersonalityProfile(traits=traits, preferences=preferences)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def delete_profile(db: Session, profile_id: str):
    profile = get_profile(db, profile_id)
    if profile:
        db.delete(profile)
        db.commit()
        return True
    return False
