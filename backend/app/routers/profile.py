from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import ProfileRequest, ProfileResponse
from ..services.profile_service import update_profile

router = APIRouter()


@router.post("/", response_model=ProfileResponse)
def profile_endpoint(payload: ProfileRequest, db: Session = Depends(get_db)):
    user = update_profile(db, payload)
    return ProfileResponse.from_orm(user)
