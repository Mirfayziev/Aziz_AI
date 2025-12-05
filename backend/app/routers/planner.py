
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.services.planner_service import create_plan

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PlannerRequest(BaseModel):
    user_id: str
    query: str | None = None


class PlannerResponse(BaseModel):
    result: str


@router.post("", response_model=PlannerResponse)
def planner_endpoint(payload: PlannerRequest, db: Session = Depends(get_db)):
    plan = create_plan(db, external_user_id=payload.user_id, query=payload.query)
    return PlannerResponse(result=plan)
