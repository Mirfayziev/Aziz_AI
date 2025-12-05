from pydantic import BaseModel
from typing import List

class MemoryAdd(BaseModel):
    text: str
    user_id: str = "aziz"
    source: str = "chat"

class MemoryOut(BaseModel):
    id: int
    text: str
    user_id: str
    source: str
    created_at: str

    class Config:
        from_attributes = True

class MemorySearchRequest(BaseModel):
    query: str
    top_k: int = 5

class MemorySearchResult(BaseModel):
    text: str
    score: float

