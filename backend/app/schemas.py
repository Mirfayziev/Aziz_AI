from pydantic import BaseModel
from typing import Optional, List, Any, Literal

# --- Core chat ---

class ChatRequest(BaseModel):
    user_external_id: str
    message: str
    model_tier: str = "default"  # fast / default / deep

class ChatResponse(BaseModel):
    reply: str

# --- Profile / personality ---

class ProfileUpdate(BaseModel):
    user_external_id: str
    name: Optional[str] = None
    bio: Optional[str] = None
    goals: Optional[List[str]] = None
    interests: Optional[List[str]] = None

class Profile(BaseModel):
    user_external_id: str
    name: Optional[str]
    bio: Optional[str]
    goals: Optional[List[str]]
    interests: Optional[List[str]]

# --- Planner / daily plans ---

class PlanCreate(BaseModel):
    user_external_id: str
    title: str
    description: Optional[str] = None
    scheduled_for: Optional[str] = None  # ISO date (YYYY-MM-DD)

class PlanOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    scheduled_for: Optional[str]

    class Config:
        from_attributes = True

# --- Audio chat ---

class AudioChatResponse(BaseModel):
    text: str
    reply: str

# --- 6-core assistant: social replies, office docs, meta tools ---

class SocialReplyRequest(BaseModel):
    user_external_id: str
    platform: Literal["telegram", "instagram", "other"] = "telegram"
    message: str
    tone: Literal["friendly", "formal", "casual", "strict"] = "friendly"
    purpose: Literal["chat", "support", "marketing", "personal"] = "chat"
    model_tier: str = "default"

class SocialReplyResponse(BaseModel):
    reply: str
    reasoning: Optional[str] = None

class OfficeDocPlanRequest(BaseModel):
    user_external_id: str
    doc_type: Literal["word", "excel", "powerpoint"]
    topic: str
    purpose: str
    details: Optional[str] = None
    model_tier: str = "default"

class OfficeDocSection(BaseModel):
    title: str
    content: str

class OfficeTableSpec(BaseModel):
    name: str
    description: str
    columns: List[str]

class OfficeDocPlanResponse(BaseModel):
    outline: List[OfficeDocSection]
    tables: List[OfficeTableSpec] = []
    notes_for_user: Optional[str] = None

class BrainQueryRequest(BaseModel):
    user_external_id: str
    question: str
    model_tier: str = "default"

class BrainQueryResponse(BaseModel):
    answer: str
    used_memories: List[str] = []

