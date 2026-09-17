import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    display_name: str = Field(..., min_length=1, max_length=100)
    age_bracket: str | None = Field(None, max_length=30)
    city: str = Field(..., min_length=1, max_length=100)
    instagram_handle: str | None = Field(None, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    display_name: str | None = Field(None, min_length=1, max_length=100)
    age_bracket: str | None = Field(None, max_length=30)
    city: str | None = Field(None, min_length=1, max_length=100)
    instagram_handle: str | None = Field(None, max_length=100)


class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

