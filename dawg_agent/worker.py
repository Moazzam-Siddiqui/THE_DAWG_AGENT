"""The clock watcher.

This program checks for posts that are due. It does nothing if publishing is OFF.
"""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler

from dawg_agent.config import get_settings
from dawg_agent.db import SessionLocal, init_db
from dawg_agent.services.events import record_event
from dawg_agent.services.instagram import publish_reel
from dawg_agent.services.publishing import publish_block_reason
from dawg_agent.services.queue import find_posts_that_are_due

logger = logging.getLogger("dawg.worker")


def publish_ready_posts() -> None:
    """Publish due posts only when the shared safety policy permits it."""
    settings = get_settings()

    if not settings.publish_enabled:
        logger.info("Publishing is OFF. Nothing will be posted.")
        return

    with SessionLocal() as database:
        for post in find_posts_that_are_due(database):
            local_now = datetime.now(ZoneInfo(settings.timezone))
            block_reason = publish_block_reason(database, post, settings, local_now)
            if block_reason:
                logger.info("Post %s remains queued: %s", post.id, block_reason)
                continue

            try:
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
                database.rollback()
                post = database.get(type(post), post.id)
                if post is None:
                    logger.exception("Post disappeared after a publishing failure.")
                    continue

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
