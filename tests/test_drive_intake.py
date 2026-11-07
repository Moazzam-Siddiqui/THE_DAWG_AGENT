"""Tests for the Google Drive local-folder handoff."""
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dawg_agent.config import Settings
from dawg_agent.db import Base
from dawg_agent.models import Post
from dawg_agent.services.drive_intake import _daily_slots, _post_id


def test_image_id_is_stable_and_content_based(tmp_path):
    first = tmp_path / "dog.jpg"
    second = tmp_path / "renamed-dog.jpg"
    first.write_bytes(b"same image bytes")
    second.write_bytes(b"same image bytes")
    assert _post_id(first).split("-")[-1] == _post_id(second).split("-")[-1]


def test_daily_slots_stay_inside_local_publish_window(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    settings = Settings(max_posts_per_day=3, timezone="Asia/Kolkata")
    now = datetime(2026, 11, 7, 6, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    slots = _daily_slots(session, settings, now)
    assert len(slots) == 3
    assert [slot.hour for slot in slots] == [7, 12, 17]
    assert all(slot.tzinfo is not None for slot in slots)
    session.close()
    engine.dispose()


def test_existing_scheduled_posts_reduce_daily_capacity(tmp_path):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False},
                           poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    local = ZoneInfo("Asia/Kolkata")
    session.add(Post(
        id="already-scheduled", image_path="dog.jpg", video_path="dog.mp4",
        status="scheduled", approved=True, idempotency_key="already-scheduled",
        scheduled_at=datetime(2026, 11, 7, 6, 30, tzinfo=ZoneInfo("UTC")),
    ))
    session.commit()
    settings = Settings(max_posts_per_day=3, timezone="Asia/Kolkata")
    now = datetime(2026, 11, 7, 6, 0, tzinfo=local)
    slots = _daily_slots(session, settings, now)
    assert len(slots) == 2
    session.close()
    engine.dispose()
