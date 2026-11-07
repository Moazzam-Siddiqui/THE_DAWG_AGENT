"""Ingest images from a Google Drive for desktop synced folder.

Google Drive for desktop performs the sync. This local process watches the
synced directory; it does not require a Drive API project or paid storage.
"""
import hashlib
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from dawg_agent.config import Settings
from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.events import record_event
from dawg_agent.services.queue import create_post, render_post

SUPPORTED_IMAGES = {".jpg", ".jpeg", ".png", ".webp"}


def _post_id(image: Path) -> str:
    digest = hashlib.sha256(image.read_bytes()).hexdigest()[:10]
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", image.stem).strip("-_")[:48] or "dog"
    return f"{stem}-{digest}"


def _daily_slots(database: Session, settings: Settings, now: datetime) -> list[datetime]:
    local_now = now.astimezone(ZoneInfo(settings.timezone))
    sh, sm = map(int, settings.publish_window_start.split(":"))
    eh, em = map(int, settings.publish_window_end.split(":"))
    start = local_now.replace(hour=sh, minute=sm, second=0, microsecond=0)
    end = local_now.replace(hour=eh, minute=em, second=0, microsecond=0)
    first = max(start, local_now + timedelta(minutes=5))
    if first >= end:
        return []

    day_start = start.replace(tzinfo=None)
    day_end = (start + timedelta(days=1)).replace(tzinfo=None)
    published = database.scalar(select(func.count()).select_from(Post).where(
        Post.status == "published", Post.updated_at >= day_start, Post.updated_at < day_end
    )) or 0
    scheduled = database.scalar(select(func.count()).select_from(Post).where(
        Post.status == "scheduled", Post.scheduled_at >= day_start, Post.scheduled_at < day_end
    )) or 0
    remaining = max(0, settings.max_posts_per_day - published - scheduled)
    if not remaining:
        return []
    span = (end - first).total_seconds()
    return [first + timedelta(seconds=span * i / remaining) for i in range(remaining)]


def ingest_drive_images(database: Session, settings: Settings) -> dict:
    incoming, processed, failed = (
        settings.drive_inbox_dir, settings.drive_processed_dir, settings.drive_failed_dir
    )
    for folder in (incoming, processed, failed, settings.output_dir):
        folder.mkdir(parents=True, exist_ok=True)

    images = sorted(
        (p for p in incoming.iterdir() if p.is_file() and p.suffix.lower() in SUPPORTED_IMAGES),
        key=lambda p: p.name.lower(),
    )
    result = {"discovered": len(images), "rendered": 0, "skipped": 0, "failed": 0}
    slots = _daily_slots(database, settings, datetime.now(ZoneInfo(settings.timezone)))
    slot_index = 0

    for image in images:
        post_id = _post_id(image)
        if database.get(Post, post_id):
            shutil.move(str(image), processed / image.name)
            result["skipped"] += 1
            continue
        if slot_index >= len(slots):
            result["skipped"] += 1
            continue
        try:
            if settings.audio_required and not settings.audio_source_path:
                raise RuntimeError("Set AUDIO_SOURCE_PATH to the campaign's What da dog doin audio.")
            details = PostCreate(
                id=post_id,
                caption=settings.default_caption,
                hashtags=settings.default_hashtags,
                image_path=str(image.resolve()),
                audio_path=str(settings.audio_source_path) if settings.audio_source_path else None,
                duration_seconds=settings.default_duration_seconds,
                scheduled_at=slots[slot_index],
                metadata={"source": "google_drive_desktop", "source_filename": image.name},
            )
            post = create_post(database, details)
            post.approved = True
            database.commit()
            render_post(database, post, settings)
            post.status = "scheduled"
            post.scheduled_at = slots[slot_index]
            database.commit()
            record_event(database, "post.auto_prepared", post.id,
                         scheduled_at=slots[slot_index].isoformat(), source_filename=image.name)
            processed_image = processed / image.name
            shutil.move(str(image), processed_image)
            post.image_path = str(processed_image.resolve())
            database.commit()
            result["rendered"] += 1
            slot_index += 1
        except Exception as error:
            database.rollback()
            if image.exists():
                shutil.move(str(image), failed / image.name)
            result["failed"] += 1
            record_event(database, "drive_ingest.failed", post_id,
                         error=str(error)[:1000], source_filename=image.name)
    return result
