from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from core.planner.models import PlannerTask
from core.planner.schema import PlannerTaskCreate, PlannerTaskResponse, AIPlanRequest, AIPlanResponse
from core.planner.service import generate_daily_plan

planner_router = APIRouter(prefix="/planner", tags=["Planner"])


@planner_router.post("/task/add", response_model=PlannerTaskResponse)
def add_task(data: PlannerTaskCreate, db: Session = Depends(get_db)):
    task = PlannerTask(
        title=data.title,
        details=data.details,
        priority=data.priority
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@planner_router.get("/task/list", response_model=list[PlannerTaskResponse])
def list_tasks(db: Session = Depends(get_db)):
    return db.query(PlannerTask).all()


@planner_router.post("/auto-plan", response_model=AIPlanResponse)
async def auto_plan(request: AIPlanRequest):
    plan = await generate_daily_plan(request.goals, request.tasks)
    return AIPlanResponse(plan=plan)
