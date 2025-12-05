from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.planner_service import generate_plan

router = APIRouter(tags=["planner"])

class PlanRequest(BaseModel):
    user_external_id: str
    query: str
    model_tier: str = "default"

class PlanResponse(BaseModel):
    result: str

@router.post("", response_model=PlanResponse)
def planner(req: PlanRequest):
    try:
        result = generate_plan(req.query, req.model_tier)
        return PlanResponse(result=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
