"""The clock watcher.

This program checks for posts that are due. It does nothing if publishing is OFF.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func, select

from dawg_agent.config import get_settings
from dawg_agent.db import SessionLocal, init_db
from dawg_agent.models import Post
from dawg_agent.services.events import record_event
from dawg_agent.services.instagram import publish_reel
from dawg_agent.services.queue import find_posts_that_are_due

logger = logging.getLogger("dawg.worker")


def is_publish_time_allowed(now: datetime, settings) -> bool:
    """Only allow posts inside the daily time window."""
    start_hour, start_minute = map(int, settings.publish_window_start.split(":"))
    end_hour, end_minute = map(int, settings.publish_window_end.split(":"))
    current_minutes = now.hour * 60 + now.minute
    start_minutes = start_hour * 60 + start_minute
    end_minutes = end_hour * 60 + end_minute
    return start_minutes <= current_minutes <= end_minutes


def has_daily_space(database, now: datetime, settings) -> bool:
    """Check whether today's post limit has already been reached."""
    today_count = database.scalar(
        select(func.count())
        .select_from(Post)
        .where(
            Post.status == "published",
            func.date(Post.updated_at) == now.date().isoformat(),
        )
    ) or 0

    if today_count >= settings.max_posts_per_day:
        logger.warning("Today's posting limit has been reached.")
        return False

    latest_post = database.scalar(
        select(Post)
        .where(Post.status == "published")
        .order_by(Post.updated_at.desc())
        .limit(1)
    )

    if latest_post and latest_post.updated_at:
        last_post_time = latest_post.updated_at
        if last_post_time.tzinfo is None:
            last_post_time = last_post_time.replace(tzinfo=ZoneInfo("UTC"))

        minutes_since_last_post = (
            datetime.now(ZoneInfo("UTC")) - last_post_time
        ).total_seconds() / 60

        if minutes_since_last_post < settings.min_post_interval_minutes:
            return False

    return True


def publish_ready_posts() -> None:
    """Publish posts whose scheduled time has arrived."""
    settings = get_settings()

    if not settings.publish_enabled:
        logger.info("Publishing is OFF. Nothing will be posted.")
        return

    with SessionLocal() as database:
        for post in find_posts_that_are_due(database):
            try:
                local_now = datetime.now(ZoneInfo(settings.timezone))

                if not is_publish_time_allowed(local_now, settings):
                    continue

                if not has_daily_space(database, local_now, settings):
                    continue

                if not post.approved or not post.media_url:
                    continue

                instagram_id = publish_reel(post.media_url, post.caption, settings)
                post.published_media_id = instagram_id
                post.status = "published"
                post.last_error = None
                database.commit()

                record_event(
                    database,
                    "post.published",
                    post.id,
                    instagram_media_id=instagram_id,
                )
                logger.info("Instagram published post %s.", post.id)

            except Exception as error:
                post.attempts += 1
                post.last_error = str(error)[:2000]

                if post.attempts > settings.max_retries:
                    post.status = "failed"

                database.commit()
                record_event(
                    database,
                    "post.publish_failed",
                    post.id,
                    error=str(error),
                    attempts=post.attempts,
                )
                logger.exception("Could not publish post %s.", post.id)


def run_worker() -> None:
    """Start checking for posts every few seconds."""
    settings = get_settings()
    init_db()
    logging.basicConfig(level=settings.log_level)

    clock = BlockingScheduler(timezone=settings.timezone)
    clock.add_job(
        publish_ready_posts,
        "interval",
        seconds=settings.scheduler_poll_seconds,
        max_instances=1,
        coalesce=True,
        id="check-for-ready-posts",
    )

    logger.info("The DAWG worker is awake. Publishing is %s.", settings.publish_enabled)
    clock.start()
