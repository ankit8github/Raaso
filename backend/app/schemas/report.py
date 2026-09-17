import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ReportCreate(BaseModel):
    reporter_id: uuid.UUID
    reported_user_id: uuid.UUID
    reason: str = Field(..., min_length=2, max_length=100)
    details: str | None = Field(None, max_length=1000)


class ReportResponse(BaseModel):
    id: uuid.UUID
    reporter_id: uuid.UUID
    reported_user_id: uuid.UUID
    reason: str
    details: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

