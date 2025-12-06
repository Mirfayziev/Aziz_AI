from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["planner"])


class PlanRequest(BaseModel):
    text: str


@router.post("/")
async def planner(req: PlanRequest):
    return {"plan": f"Reja yaratildi: {req.text}"}
