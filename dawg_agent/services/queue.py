"""Move posts from one step to the next.

This file is the traffic controller. It does not make videos itself.
It asks the video maker or upload helper to do that work.
"""
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.events import record_event


class QueueError(RuntimeError):
    """Raised when someone tries to move a post in the wrong order."""


def create_post(database: Session, post_details: PostCreate) -> Post:
    """Put a new post on the waiting list."""
    if database.get(Post, post_details.id):
        raise QueueError(f"The post ID '{post_details.id}' is already being used.")

    post = Post(
        id=post_details.id,
        caption=post_details.caption,
        hashtags_json=json.dumps(post_details.hashtags),
        image_path=post_details.image_path,
        audio_path=post_details.audio_path,
        duration_seconds=post_details.duration_seconds,
        scheduled_at=post_details.scheduled_at,
        metadata_json=json.dumps(post_details.metadata),
        idempotency_key=post_details.id,
    )

    database.add(post)
    database.commit()
    database.refresh(post)
    record_event(database, "post.created", post.id)
    return post


def approve_post(database: Session, post: Post) -> Post:
    """Mark a draft as approved by a human."""
    if post.status in {"published", "failed"}:
        raise QueueError(f"This post cannot be approved because its status is '{post.status}'.")

    post.approved = True
    post.status = "approved"
    database.commit()
    database.refresh(post)
    record_event(database, "post.approved", post.id)
    return post


def render_post(database: Session, post: Post, settings) -> Post:
    """Turn the post's picture into an MP4 video."""
    from dawg_agent.services.render import render_reel

    if settings.require_approval and not post.approved:
        raise QueueError("Approve this post before making its video.")

    audio_path = post.audio_path or settings.audio_source_path
    video_path = settings.output_dir / f"{post.id}.mp4"

    render_reel(
        image_path=post.image_path,
        output_path=video_path,
        duration=post.duration_seconds,
        settings=settings,
        audio_path=audio_path,
    )

    post.video_path = str(video_path)
    post.status = "rendered"
    post.last_error = None
    database.commit()
    database.refresh(post)
    record_event(database, "post.rendered", post.id, video_path=str(video_path))
    return post


def upload_post(database: Session, post: Post, settings) -> Post:
    """Send the finished MP4 to Cloudinary."""
    from dawg_agent.services.cloudinary import upload_video

    if not post.approved:
        raise QueueError("Approve this post before uploading it.")
    if not post.video_path:
        raise QueueError("Make the video before uploading it.")

    post.media_url = upload_video(post.video_path, settings)
    post.status = "uploaded"
    database.commit()
    database.refresh(post)
    record_event(database, "post.uploaded", post.id, media_url=post.media_url)
    return post


def schedule_post(database: Session, post: Post, publish_time: datetime) -> Post:
    """Put an uploaded post on the calendar."""
    if not post.approved:
        raise QueueError("Approve this post before scheduling it.")
    if post.status not in {"uploaded", "scheduled"} or not post.media_url:
        raise QueueError("Upload the video before scheduling it.")
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
    """Find approved posts whose scheduled time has arrived."""
    now = datetime.now(timezone.utc)
    query = select(Post).where(
        Post.status == "scheduled",
        Post.approved.is_(True),
        Post.scheduled_at <= now,
    )
    return list(database.scalars(query).all())
