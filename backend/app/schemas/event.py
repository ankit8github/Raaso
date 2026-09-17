import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class EventBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    city: str = Field(..., min_length=1, max_length=100)
    venue: str = Field(..., min_length=1, max_length=200)
    starts_at: datetime
    ends_at: datetime | None = None
    ticket_url: str | None = None
    is_active: bool = True


class EventCreate(EventBase):
    pass


class EventResponse(EventBase):
    id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

