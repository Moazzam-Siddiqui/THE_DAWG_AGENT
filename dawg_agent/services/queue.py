import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.events import record_event


class QueueError(RuntimeError):
    pass


def create_post(db: Session, data: PostCreate) -> Post:
    if db.get(Post, data.id):
        raise QueueError(f"Post '{data.id}' already exists.")
    post = Post(
        id=data.id, caption=data.caption, hashtags_json=json.dumps(data.hashtags),
        image_path=data.image_path, audio_path=data.audio_path,
        duration_seconds=data.duration_seconds, scheduled_at=data.scheduled_at,
        metadata_json=json.dumps(data.metadata), idempotency_key=data.id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    record_event(db, "post.created", post.id)
    return post


def approve_post(db: Session, post: Post) -> Post:
    if post.status in {"published", "failed"}:
        raise QueueError(f"Cannot approve a post in state '{post.status}'.")
    post.approved = True
    post.status = "approved"
    db.commit()
    db.refresh(post)
    record_event(db, "post.approved", post.id)
    return post


def render_post(db: Session, post: Post, settings) -> Post:
    from dawg_agent.services.render import render_reel
    if settings.require_approval and not post.approved:
        raise QueueError("Post must be approved before rendering.")
    audio = post.audio_path or (str(settings.audio_source_path) if settings.audio_source_path else None)
    output = settings.output_dir / f"{post.id}.mp4"
    render_reel(post.image_path, output, post.duration_seconds, settings, audio)
    post.video_path = str(output)
    post.status = "rendered"
    post.last_error = None
    db.commit()
    db.refresh(post)
    record_event(db, "post.rendered", post.id, video_path=str(output))
    return post


def upload_post(db: Session, post: Post, settings) -> Post:
    from dawg_agent.services.cloudinary import upload_video
    if not post.approved:
        raise QueueError("Post must be approved before upload.")
    if not post.video_path:
        raise QueueError("Render the post before uploading.")
    post.media_url = upload_video(post.video_path, settings)
    post.status = "uploaded"
    db.commit()
    db.refresh(post)
    record_event(db, "post.uploaded", post.id, media_url=post.media_url)
    return post


def schedule_post(db: Session, post: Post, scheduled_at) -> Post:
    from datetime import datetime, timezone
    if not post.approved:
        raise QueueError("Post must be approved before scheduling.")
    if post.status not in {"uploaded", "scheduled"} or not post.media_url:
        raise QueueError("Post must be uploaded before scheduling.")
    if scheduled_at.tzinfo is None:
        raise QueueError("scheduled_at must include a timezone.")
    if scheduled_at <= datetime.now(timezone.utc):
        raise QueueError("scheduled_at must be in the future.")
    post.scheduled_at = scheduled_at
    post.status = "scheduled"
    db.commit()
    db.refresh(post)
    record_event(db, "post.scheduled", post.id, scheduled_at=scheduled_at.isoformat())
    return post


def due_posts(db: Session):
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return list(db.scalars(select(Post).where(Post.status == "scheduled", Post.approved.is_(True),
                                               Post.scheduled_at <= now)).all())
