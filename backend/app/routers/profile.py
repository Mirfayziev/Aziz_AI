from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["profile"])

class ProfileRequest(BaseModel):
    traits: dict
    preferences: dict


@router.post("/")
async def update_profile(req: ProfileRequest):
    return {"status": "updated", "data": req.dict()}
