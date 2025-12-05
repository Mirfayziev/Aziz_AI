from pydantic import BaseModel
from typing import Optional, List, Any

class ChatRequest(BaseModel):
    user_external_id: str
    message: str
    model_tier: str = "default"  # fast / default / deep

class ChatResponse(BaseModel):
    reply: str

class ProfileUpdate(BaseModel):
    user_external_id: str
    name: Optional[str] = None
    bio: Optional[str] = None
    goals: Optional[list[str]] = None
    interests: Optional[list[str]] = None

class Profile(BaseModel):
    user_external_id: str
    name: Optional[str]
    bio: Optional[str]
    goals: Optional[list[str]]
    interests: Optional[list[str]]

class PlanCreate(BaseModel):
    user_external_id: str
    title: str
    description: Optional[str] = None
    scheduled_for: Optional[str] = None

class PlanOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    scheduled_for: Optional[str]

    class Config:
        from_attributes = True

class AudioChatResponse(BaseModel):
    text: str
    reply: str
