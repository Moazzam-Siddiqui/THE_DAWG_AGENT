"""Move posts through the local production and publishing queue."""
import json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.events import record_event

class QueueError(RuntimeError):
    """Raised when a post moves out of sequence."""

def create_post(database: Session, post_details: PostCreate) -> Post:
    if database.get(Post, post_details.id):
        raise QueueError(f"Post ID '{post_details.id}' already exists.")
    post = Post(
        id=post_details.id, caption=post_details.caption,
        hashtags_json=json.dumps(post_details.hashtags), image_path=post_details.image_path,
        audio_path=post_details.audio_path, duration_seconds=post_details.duration_seconds,
        scheduled_at=post_details.scheduled_at, metadata_json=json.dumps(post_details.metadata),
        idempotency_key=post_details.id,
    )
    database.add(post)
    database.commit()
    database.refresh(post)
    record_event(database, "post.created", post.id)
    return post

def approve_post(database: Session, post: Post) -> Post:
    if post.status in {"published", "failed"}:
        raise QueueError(f"Cannot approve a post with status '{post.status}'.")
    post.approved = True
    post.status = "approved"
    database.commit()
    database.refresh(post)
    record_event(database, "post.approved", post.id)
    return post

def render_post(database: Session, post: Post, settings) -> Post:
    from dawg_agent.services.render import render_reel
    if settings.require_approval and not post.approved:
        raise QueueError("Approve this post before rendering.")
    audio_path = post.audio_path or settings.audio_source_path
    video_path = settings.output_dir / f"{post.id}.mp4"
    render_reel(post.image_path, video_path, post.duration_seconds, settings, audio_path)
    post.video_path = str(video_path)
    post.status = "rendered"
    post.last_error = None
    database.commit()
    database.refresh(post)
    record_event(database, "post.rendered", post.id, video_path=str(video_path))
    return post

def schedule_post(database: Session, post: Post, publish_time: datetime) -> Post:
    if not post.approved:
        raise QueueError("Post must pass the automatic validation/approval gate.")
    if post.status not in {"rendered", "scheduled"} or not post.video_path:
        raise QueueError("Render the video before scheduling it.")
    if publish_time.tzinfo is None:
        raise QueueError("Include a timezone in the scheduled date and time.")
    if publish_time <= datetime.now(timezone.utc):
        raise QueueError("Choose a time in the future.")
    post.scheduled_at = publish_time
    post.status = "scheduled"
    database.commit()
    database.refresh(post)
    record_event(database, "post.scheduled", post.id, publish_time=publish_time.isoformat())
    return post

def find_posts_that_are_due(database: Session) -> list[Post]:
    now = datetime.now(timezone.utc)
    query = select(Post).where(
        Post.status == "scheduled", Post.approved.is_(True), Post.scheduled_at <= now
    )
    return list(database.scalars(query).all())
