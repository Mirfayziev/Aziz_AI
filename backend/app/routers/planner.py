from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import PlannerRequest, PlannerResponse
from ..services.planner_service import create_plan

router = APIRouter()


@router.post("/", response_model=PlannerResponse)
def planner_endpoint(payload: PlannerRequest, db: Session = Depends(get_db)):
    plan, date_str = create_plan(
        db=db,
        external_user_id=payload.user_id,
        text=payload.text,
        mode=payload.mode,
    )
    return PlannerResponse(plan_text=plan, mode=payload.mode, date_str=date_str)
