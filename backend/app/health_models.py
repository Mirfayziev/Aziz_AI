from pydantic import BaseModel
from datetime import datetime

class HealthRecordCreate(BaseModel):
    user_external_id: str
    metric_type: str
    value: float
    unit: str
    recorded_at: datetime

class HealthRecordOut(HealthRecordCreate):
    id: int

    class Config:
        from_attributes = True
