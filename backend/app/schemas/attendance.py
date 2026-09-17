import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class AttendanceBase(BaseModel):
    intent: str = Field(..., min_length=1, max_length=50)
    dance_level: str = Field(..., min_length=1, max_length=50)
    vibes: str | None = None
    group_size_preference: int | None = Field(None, ge=1, le=20)


class AttendanceCreate(AttendanceBase):
    user_id: uuid.UUID
    event_id: uuid.UUID

class AttendanceUpdate(BaseModel):
    intent: str | None = Field(None, min_length=1, max_length=50)
    dance_level: str | None = Field(None, min_length=1, max_length=50)
    vibes: str | None = None
    group_size_preference: int | None = Field(None, ge=1, le=20)

class AttendanceResponse(AttendanceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    event_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceWithUserResponse(AttendanceResponse):
    user: UserResponse

    model_config = ConfigDict(from_attributes=True)

