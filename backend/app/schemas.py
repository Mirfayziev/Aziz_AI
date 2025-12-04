from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel, EmailStr


# --- Users & Auth ---
class UserBase(BaseModel):
    full_name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    bio: Optional[str] = None
    goals: Optional[str] = None
    interests: Optional[str] = None
    personality: Optional[str] = None
    timezone: Optional[str] = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    goals: Optional[str] = None
    interests: Optional[str] = None
    personality: Optional[str] = None
    timezone: Optional[str] = None


# --- Chat & Memory ---
class ChatRequest(BaseModel):
    chat_id: str
    message: str


class ChatReply(BaseModel):
    reply: str


class MemoryOut(BaseModel):
    id: int
    chat_id: str
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True


# --- Planner ---
class DayPlanRequest(BaseModel):
    date: Optional[date] = None
    goals: Optional[List[str]] = None


class DayPlanItem(BaseModel):
    time: str
    title: str
    note: Optional[str] = None


class DayPlanResponse(BaseModel):
    date: date
    items: List[DayPlanItem]


# --- Daily Summary ---
class DailySummaryRequest(BaseModel):
    chat_id: str
    date: Optional[date] = None


class DailySummaryResponse(BaseModel):
    date: date
    summary: str
