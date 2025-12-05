from pydantic import BaseModel
from typing import Optional, List

class PlannerTaskCreate(BaseModel):
    title: str
    details: Optional[str] = None
    priority: int = 1
    deadline: Optional[str] = None


class PlannerTaskResponse(BaseModel):
    id: int
    title: str
    details: Optional[str]
    priority: int
    status: str

    class Config:
        orm_mode = True


class AIPlanRequest(BaseModel):
    goals: str
    tasks: List[str]


class AIPlanResponse(BaseModel):
    plan: str
