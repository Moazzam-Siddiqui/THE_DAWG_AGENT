"""One publishing policy shared by the API and background worker.

Every route that can publish a Reel must pass through this module first.
Keeping the rules in one place prevents the API and worker from drifting apart.
"""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from dawg_agent.config import Settings
from dawg_agent.models import Post


def publish_block_reason(
    database: Session,
    post: Post,
    settings: Settings,
    now: datetime | None = None,
) -> str | None:
    """Return why publishing is blocked, or None when the post may be published."""
    if not settings.publish_enabled:
        return "Publishing is switched OFF."

    if not post.approved:
        return "This post has not been approved by a person."

    if not post.media_url:
        return "This post has no uploaded video URL."

    if post.status not in {"uploaded", "scheduled"}:
        return f"A post with status '{post.status}' cannot be published."

    local_now = now or datetime.now(ZoneInfo(settings.timezone))
    if local_now.tzinfo is None:
        raise ValueError("The publishing policy requires a timezone-aware clock.")

    start_hour, start_minute = map(int, settings.publish_window_start.split(":"))
    end_hour, end_minute = map(int, settings.publish_window_end.split(":"))
    current_time = local_now.timetz().replace(tzinfo=None)
    if not time(start_hour, start_minute) <= current_time <= time(end_hour, end_minute):
        return (
            "The current time is outside the publishing window "
            f"({settings.publish_window_start}–{settings.publish_window_end} "
            f"{settings.timezone})."
        )

    local_day_start = datetime.combine(local_now.date(), time.min, tzinfo=local_now.tzinfo)
    local_day_end = local_day_start + timedelta(days=1)
    utc_day_start = local_day_start.astimezone(timezone.utc).replace(tzinfo=None)
    utc_day_end = local_day_end.astimezone(timezone.utc).replace(tzinfo=None)

    # Count posts using UTC boundaries derived from the configured local day.
    from sqlalchemy import func

    published_count = database.scalar(
        select(func.count())
        .select_from(Post)
        .where(
            Post.status == "published",
            Post.updated_at >= utc_day_start,
            Post.updated_at < utc_day_end,
        )
    ) or 0
    if published_count >= settings.max_posts_per_day:
        return "Today's publishing limit has been reached."

    latest_post = database.scalar(
        select(Post)
        .where(Post.status == "published")
        .order_by(Post.updated_at.desc())
        .limit(1)
    )
    if latest_post and latest_post.updated_at:
        last_published_at = latest_post.updated_at
        if last_published_at.tzinfo is None:
            last_published_at = last_published_at.replace(tzinfo=timezone.utc)

        minutes_since_last_post = (
            local_now.astimezone(timezone.utc) - last_published_at.astimezone(timezone.utc)
        ).total_seconds() / 60
        if minutes_since_last_post < settings.min_post_interval_minutes:
            remaining = settings.min_post_interval_minutes - minutes_since_last_post
            return f"Minimum posting interval has not elapsed ({remaining:.0f} minutes remain)."

    return None
