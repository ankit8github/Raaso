import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserResponse


class SquadBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    max_members: int = Field(default=6, ge=2, le=30)


class SquadCreate(SquadBase):
    event_id: uuid.UUID
    created_by: uuid.UUID


class SquadMemberResponse(BaseModel):
    id: uuid.UUID
    squad_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    joined_at: datetime
    user: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class SquadResponse(SquadBase):
    id: uuid.UUID
    event_id: uuid.UUID
    created_by: uuid.UUID
    status: str
    created_at: datetime
    member_count: int = 0
    whatsapp_link: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SquadDetailResponse(SquadResponse):
    members: list[SquadMemberResponse] = []
    creator: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)


class SquadJoinRequest(BaseModel):
    user_id: uuid.UUID


class SquadLeaveRequest(BaseModel):
    user_id: uuid.UUID

