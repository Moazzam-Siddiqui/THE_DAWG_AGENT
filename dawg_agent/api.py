"""The robot's control panel.

Open http://127.0.0.1:8000/docs after starting the API to try these controls.
"""
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from dawg_agent.config import get_settings
from dawg_agent.db import SessionLocal, init_db
from dawg_agent.models import Event, Post
from dawg_agent.schemas import EventRead, PostCreate, PostRead, ScheduleRequest
from dawg_agent.services.events import record_event
from dawg_agent.services.publishing import publish_block_reason
from dawg_agent.services.queue import (
    QueueError,
    approve_post,
    create_post,
    render_post,
    schedule_post,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Prepare the database when the API starts."""
    init_db()
    yield


app = FastAPI(
    title="THE DAWG AGENT",
    description="A small control panel for making and managing dog Reels.",
    version="0.2.0",
    lifespan=lifespan,
)


def get_database():
    """Give one API request a database connection."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def check_api_key(x_api_key: str | None = Header(default=None)):
    """Check the API password when one has been configured."""
    saved_key = get_settings().api_key
    if saved_key and not secrets.compare_digest(x_api_key or "", saved_key):
        raise HTTPException(status_code=401, detail="The API key is not correct.")


def find_post_or_error(database: Session, post_id: str) -> Post:
    """Find a post, or tell the user it does not exist."""
    post = database.get(Post, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="I could not find that post.")
    return post


@app.get("/health", summary="Is the robot awake?")
def health():
    settings = get_settings()
    return {
        "status": "awake",
        "publishing_is_on": settings.publish_enabled,
        "instagram_details_are_ready": settings.instagram_is_ready,
    }


@app.get("/posts", response_model=list[PostRead], dependencies=[Depends(check_api_key)])
def list_posts(database: Session = Depends(get_database)):
    """Show all posts, newest first."""
    query = select(Post).order_by(Post.created_at.desc())
    return list(database.scalars(query).all())


@app.post("/posts", response_model=PostRead, status_code=201,
          dependencies=[Depends(check_api_key)])
def add_post(details: PostCreate, database: Session = Depends(get_database)):
    """Add a new post to the waiting list."""
    try:
        return create_post(database, details)
    except QueueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/posts/{post_id}/approve", response_model=PostRead,
          dependencies=[Depends(check_api_key)])
def approve(post_id: str, database: Session = Depends(get_database)):
    """Tell the robot that a person has checked and approved this post."""
    try:
        return approve_post(database, find_post_or_error(database, post_id))
    except QueueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@app.post("/posts/{post_id}/render", response_model=PostRead,
          dependencies=[Depends(check_api_key)])
def render(post_id: str, database: Session = Depends(get_database)):
    """Make an MP4 video from the post's picture."""
    try:
        return render_post(database, find_post_or_error(database, post_id), get_settings())
    except (QueueError, RuntimeError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/posts/{post_id}/schedule", response_model=PostRead,
          dependencies=[Depends(check_api_key)])
def schedule(post_id: str, details: ScheduleRequest,
             database: Session = Depends(get_database)):
    """Choose when an uploaded post should go live."""
    try:
        return schedule_post(
            database,
            find_post_or_error(database, post_id),
            details.scheduled_at,
        )
    except QueueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/posts/{post_id}/publish", response_model=PostRead,
          dependencies=[Depends(check_api_key)])
def publish_now(post_id: str, database: Session = Depends(get_database)):
    """Publish now, but never bypass the worker's publishing safety rules."""
    from dawg_agent.services.instagram import publish_reel

    settings = get_settings()
    post = find_post_or_error(database, post_id)
    block_reason = publish_block_reason(database, post, settings)
    if block_reason:
        status_code = 403 if not settings.publish_enabled else 409
        raise HTTPException(status_code=status_code, detail=block_reason)

    try:
        instagram_id = publish_reel(post.video_path, post.caption, settings)
        post.published_media_id = instagram_id
        post.status = "published"
        post.last_error = None
        database.commit()
        record_event(database, "post.published", post.id, instagram_media_id=instagram_id)
        database.refresh(post)
        return post
    except RuntimeError as error:
        database.rollback()
        raise HTTPException(status_code=502, detail=str(error)) from error


@app.get("/events", response_model=list[EventRead], dependencies=[Depends(check_api_key)])
def show_events(database: Session = Depends(get_database), limit: int = 100):
    """Show the robot's activity diary."""
    safe_limit = max(1, min(limit, 500))
    query = select(Event).order_by(Event.created_at.desc()).limit(safe_limit)
    return list(database.scalars(query).all())
