"""Tests for the shared publishing safety policy."""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from dawg_agent.config import Settings
from dawg_agent.db import Base
from dawg_agent.models import Post
from dawg_agent.services.publishing import publish_block_reason


@pytest.fixture
def database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    yield session
    session.close()
    engine.dispose()


def ready_post(database, **overrides):
    values = {
        "id": "policy-test",
        "caption": "A dog being a dog",
        "image_path": "assets/inbox/dog.jpg",
        "status": "scheduled",
        "approved": True,
        "media_url": "https://example.com/dog.mp4",
        "idempotency_key": "policy-test",
    }
    values.update(overrides)
    post = Post(**values)
    database.add(post)
    database.commit()
    return post


def test_publishing_disabled_blocks_every_post(database):
    settings = Settings(publish_enabled=False)
    post = ready_post(database)
    now = datetime(2026, 11, 7, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    assert publish_block_reason(database, post, settings, now) == "Publishing is switched OFF."


def test_post_outside_local_window_is_blocked(database):
    settings = Settings(publish_enabled=True)
    post = ready_post(database)
    now = datetime(2026, 11, 7, 6, 59, tzinfo=ZoneInfo("Asia/Kolkata"))

    reason = publish_block_reason(database, post, settings, now)

    assert reason is not None
    assert "outside the publishing window" in reason


def test_unapproved_post_is_blocked(database):
    settings = Settings(publish_enabled=True)
    post = ready_post(database, approved=False)
    now = datetime(2026, 11, 7, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))

    assert publish_block_reason(database, post, settings, now) == (
        "This post has not been approved by a person."
    )


def test_daily_limit_counts_posts_in_the_configured_local_day(database):
    settings = Settings(publish_enabled=True, max_posts_per_day=1)
    now = datetime(2026, 11, 7, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    published_at = now.astimezone(ZoneInfo("UTC")).replace(tzinfo=None)
    ready_post(
        database,
        id="already-published",
        idempotency_key="already-published",
        status="published",
        updated_at=published_at,
    )
    post = ready_post(database, id="next-post", idempotency_key="next-post")

    assert publish_block_reason(database, post, settings, now) == (
        "Today's publishing limit has been reached."
    )


def test_minimum_interval_is_enforced(database):
    settings = Settings(publish_enabled=True, min_post_interval_minutes=180)
    now = datetime(2026, 11, 7, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata"))
    ready_post(
        database,
        id="just-published",
        idempotency_key="just-published",
        status="published",
        updated_at=(now - timedelta(minutes=30)).astimezone(ZoneInfo("UTC")).replace(tzinfo=None),
    )
    post = ready_post(database, id="next-post", idempotency_key="next-post")

    reason = publish_block_reason(database, post, settings, now)

    assert reason is not None
    assert "Minimum posting interval" in reason


def test_naive_clock_is_rejected(database):
    settings = Settings(publish_enabled=True)
    post = ready_post(database)

    with pytest.raises(ValueError, match="timezone-aware"):
        publish_block_reason(database, post, settings, datetime(2026, 11, 7, 12, 0))
