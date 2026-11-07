"""Check information before the API lets it into the robot."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
    """Information needed to create a new draft post."""

    id: str = Field(min_length=1, max_length=80)
    caption: str = Field(default="", max_length=2200)
    hashtags: list[str] = Field(default_factory=list, max_length=30)
    image_path: str
    audio_path: str | None = None
    duration_seconds: int = Field(default=9, ge=6, le=12)
    scheduled_at: datetime | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PostRead(BaseModel):
    """Information the API sends back about a post."""

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
    """The date and time when a post should be published."""

    scheduled_at: datetime


class EventRead(BaseModel):
    """One entry from the robot's activity diary."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: str | None
    event_type: str
    details: str
    created_at: datetime
