"""One set of safety rules shared by every publishing path."""
from datetime import datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dawg_agent.config import Settings
from dawg_agent.models import Post


def publish_block_reason(database: Session, post: Post, settings: Settings,
                         now: datetime | None = None) -> str | None:
    if not settings.publish_enabled:
        return "Publishing is switched OFF."
    if settings.require_approval and not post.approved:
        return "This post has not been approved."
    if not post.video_path:
        return "This post has no local rendered video."
    if post.status != "scheduled":
        return f"A post with status '{post.status}' cannot be published."

    local_now = now or datetime.now(ZoneInfo(settings.timezone))
    if local_now.tzinfo is None:
        raise ValueError("The publishing policy requires a timezone-aware clock.")
    sh, sm = map(int, settings.publish_window_start.split(":"))
    eh, em = map(int, settings.publish_window_end.split(":"))
    clock_time = local_now.timetz().replace(tzinfo=None)
    if not time(sh, sm) <= clock_time <= time(eh, em):
        return f"Outside publishing window ({settings.publish_window_start}–{settings.publish_window_end} {settings.timezone})."

    midnight = datetime.combine(local_now.date(), time.min, tzinfo=local_now.tzinfo)
    tomorrow = midnight + timedelta(days=1)
    utc_start = midnight.astimezone(timezone.utc).replace(tzinfo=None)
    utc_end = tomorrow.astimezone(timezone.utc).replace(tzinfo=None)
    count = database.scalar(select(func.count()).select_from(Post).where(
        Post.status == "published", Post.updated_at >= utc_start, Post.updated_at < utc_end
    )) or 0
    if count >= settings.max_posts_per_day:
        return "Today's publishing limit has been reached."

    latest = database.scalar(select(Post).where(Post.status == "published")
                             .order_by(Post.updated_at.desc()).limit(1))
    if latest and latest.updated_at:
        last = latest.updated_at
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        elapsed = (local_now.astimezone(timezone.utc) - last.astimezone(timezone.utc)).total_seconds() / 60
        if elapsed < settings.min_post_interval_minutes:
            return f"Minimum posting interval: {settings.min_post_interval_minutes - elapsed:.0f} minutes remain."
    return None
