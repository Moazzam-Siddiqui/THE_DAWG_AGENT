from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator

class PostCreate(BaseModel):
    id: str = Field(min_length=1, max_length=80)
    caption: str = Field(default="", max_length=2200)
    hashtags: list[str] = Field(default_factory=list, max_length=30)
    image_path: str
    audio_path: str | None = None
    duration_seconds: int = Field(default=9, ge=6, le=12)
    scheduled_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    @field_validator("image_path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("image_path is required")
        return value

class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    caption: str
    image_path: str
    audio_path: str | None
    video_path: str | None
    media_url: str | None
    duration_seconds: int
    status: str
    approved: bool
    scheduled_at: datetime | None
    attempts: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime

class ScheduleRequest(BaseModel):
    scheduled_at: datetime

class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: str | None
    event_type: str
    details: str
    created_at: datetime
