"""The shape of the information saved in the database."""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from dawg_agent.db import Base


def current_time() -> datetime:
    """Return the current time in UTC."""
    return datetime.now(timezone.utc)


class Post(Base):
    """One dog picture and everything we know about its Reel."""

    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    caption: Mapped[str] = mapped_column(Text, default="")
    hashtags_json: Mapped[str] = mapped_column(Text, default="[]")

    image_path: Mapped[str] = mapped_column(Text)
    audio_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    duration_seconds: Mapped[int] = mapped_column(Integer, default=9)
    status: Mapped[str] = mapped_column(String(24), default="draft", index=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    published_media_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_time)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=current_time,
        onupdate=current_time,
    )


class Event(Base):
    """A diary entry: what happened, to which post, and when."""

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    details: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=current_time)
