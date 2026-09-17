import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.attendance import AttendanceResponse
from app.schemas.user import UserResponse


class MatchScoreBreakdown(BaseModel):
    intent_score: int
    dance_level_score: int
    vibes_score: int
    group_size_score: int
    reasons: list[str]


class MatchResponse(BaseModel):
    id: uuid.UUID
    attendance_id: uuid.UUID
    matched_attendance_id: uuid.UUID
    score: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MatchDetailResponse(BaseModel):
    id: uuid.UUID | None = None
    attendance_id: uuid.UUID
    matched_attendance_id: uuid.UUID
    score: int
    status: str = "active"
    matched_user: UserResponse
    matched_attendance: AttendanceResponse
    reasons: list[str] = []
    whatsapp_link: str | None = None

    model_config = ConfigDict(from_attributes=True)

