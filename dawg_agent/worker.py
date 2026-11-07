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
from dawg_agent.services.queue import due_posts

logger = logging.getLogger("dawg.worker")

def _publish_due() -> None:
    cfg = get_settings()
    if not cfg.publish_enabled:
        logger.info("Publishing is disabled; scheduled posts remain queued.")
        return
    with SessionLocal() as db:
        for post in due_posts(db):
            try:
                now = datetime.now(ZoneInfo(cfg.timezone))
                start = tuple(map(int, cfg.publish_window_start.split(":")))
                end = tuple(map(int, cfg.publish_window_end.split(":")))
                minute = now.hour * 60 + now.minute
                if not (start[0]*60+start[1] <= minute <= end[0]*60+end[1]):
                    continue
                count = db.scalar(select(func.count()).select_from(Post).where(
                    Post.status == "published",
                    func.date(Post.updated_at) == now.date().isoformat())) or 0
                if count >= cfg.max_posts_per_day:
                    logger.warning("Daily publish cap reached.")
                    continue
                recent = db.scalar(select(Post).where(Post.status == "published")
                    .order_by(Post.updated_at.desc()).limit(1))
                if recent and recent.updated_at:
                    last = recent.updated_at
                    if last.tzinfo is None:
                        last = last.replace(tzinfo=ZoneInfo("UTC"))
                    if (datetime.now(ZoneInfo("UTC")) - last).total_seconds()/60 < cfg.min_post_interval_minutes:
                        continue
                if not post.media_url or not post.approved:
                    continue
                media_id = publish_reel(post.media_url, post.caption, cfg)
                post.published_media_id, post.status, post.last_error = media_id, "published", None
                db.commit()
                record_event(db, "post.published", post.id, instagram_media_id=media_id)
                logger.info("Published %s", post.id)
            except Exception as exc:
                post.attempts += 1
                post.last_error = str(exc)[:2000]
                post.status = "failed" if post.attempts > cfg.max_retries else "scheduled"
                db.commit()
                record_event(db, "post.publish_failed", post.id, error=str(exc), attempts=post.attempts)
                logger.exception("Publish failed for %s", post.id)

def run_worker() -> None:
    cfg = get_settings()
    init_db()
    logging.basicConfig(level=cfg.log_level)
    scheduler = BlockingScheduler(timezone=cfg.timezone)
    scheduler.add_job(_publish_due, "interval", seconds=cfg.scheduler_poll_seconds,
        max_instances=1, coalesce=True, id="publish-due")
    logger.info("Worker started; publishing_enabled=%s", cfg.publish_enabled)
    scheduler.start()
