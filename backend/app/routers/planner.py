from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db import get_db
from app.services.assistant_service import generate_tomorrow_plan

router = APIRouter(prefix="/api/planner", tags=["planner"])


class PlanRequest(BaseModel):
    user_external_id: str


@router.post("/tomorrow")
async def planner(req: PlanRequest, db: Session = Depends(get_db)):
    try:
        return await generate_tomorrow_plan(db, req.user_external_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
