from datetime import datetime
from typing import Optional, List, Any

from pydantic import BaseModel


class ChatRequest(BaseModel):
    user_id: str
    message: str
    model_tier: Optional[str] = "default"


class ChatResponse(BaseModel):
    reply: str
    used_model: str
    memory_used: bool = True


class PlannerRequest(BaseModel):
    user_id: str
    text: str
    mode: str = "today"  # today / tomorrow / week


class PlannerResponse(BaseModel):
    plan_text: str
    mode: str
    date_str: str


class MemoryItem(BaseModel):
    id: int
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class ProfileRequest(BaseModel):
    user_id: str
    name: Optional[str] = None
    language: Optional[str] = None


class ProfileResponse(BaseModel):
    id: int
    external_id: str
    name: Optional[str]
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
