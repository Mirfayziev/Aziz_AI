from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.planner_service import generate_plan

router = APIRouter(tags=["planner"])

class PlanRequest(BaseModel):
    user_external_id: str
    query: str     # masalan: "bugungi reja", "ertangi ishlar"
    model_tier: str = "default"

class PlanResponse(BaseModel):
    result: str

@router.post("", response_model=PlanResponse)
def planner(req: PlanRequest):
    try:
        output = generate_plan(
            query=req.query,
            model_tier=req.model_tier
        )
        return PlanResponse(result=output)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
