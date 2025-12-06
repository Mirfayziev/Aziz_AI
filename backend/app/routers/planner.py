from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from ..db import get_db
from ..schemas import PlanCreate, PlanOut
from ..services.planner_service import create_plan, get_today_plans

router = APIRouter(tags=["planner"])

@router.post("", response_model=PlanOut)
def create_plan_endpoint(req: PlanCreate, db: Session = Depends(get_db)):
    plan = create_plan(db, req.user_external_id, req.title, req.description, req.scheduled_for)
    return plan

@router.get("/today/{external_id}", response_model=List[PlanOut])
def today_plans(external_id: str, db: Session = Depends(get_db)):
    return get_today_plans(db, external_id)
