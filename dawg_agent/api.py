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
from dawg_agent.services.queue import (QueueError, approve_post, create_post, render_post,
    schedule_post, upload_post)

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(title="THE DAWG AGENT", version="0.1.0", lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_api_key(x_api_key: str | None = Header(default=None)):
    expected = get_settings().api_key
    if expected and not secrets.compare_digest(x_api_key or "", expected):
        raise HTTPException(status_code=401, detail="Invalid API key.")

def get_post(db: Session, post_id: str) -> Post:
    post = db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")
    return post

@app.get("/health")
def health():
    cfg = get_settings()
    return {"status": "ok", "publishing_enabled": cfg.publish_enabled,
        "instagram_configured": cfg.instagram_configured,
        "cloudinary_configured": cfg.cloudinary_configured}

@app.get("/posts", response_model=list[PostRead], dependencies=[Depends(check_api_key)])
def list_posts(db: Session = Depends(get_db)):
    return list(db.scalars(select(Post).order_by(Post.created_at.desc())).all())

@app.post("/posts", response_model=PostRead, status_code=201, dependencies=[Depends(check_api_key)])
def add_post(payload: PostCreate, db: Session = Depends(get_db)):
    try:
        return create_post(db, payload)
    except QueueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@app.post("/posts/{post_id}/approve", response_model=PostRead, dependencies=[Depends(check_api_key)])
def approve(post_id: str, db: Session = Depends(get_db)):
    try:
        return approve_post(db, get_post(db, post_id))
    except QueueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

@app.post("/posts/{post_id}/render", response_model=PostRead, dependencies=[Depends(check_api_key)])
def render(post_id: str, db: Session = Depends(get_db)):
    try:
        return render_post(db, get_post(db, post_id), get_settings())
    except (QueueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/posts/{post_id}/upload", response_model=PostRead, dependencies=[Depends(check_api_key)])
def upload(post_id: str, db: Session = Depends(get_db)):
    try:
        return upload_post(db, get_post(db, post_id), get_settings())
    except (QueueError, RuntimeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/posts/{post_id}/schedule", response_model=PostRead, dependencies=[Depends(check_api_key)])
def schedule(post_id: str, payload: ScheduleRequest, db: Session = Depends(get_db)):
    try:
        return schedule_post(db, get_post(db, post_id), payload.scheduled_at)
    except QueueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/posts/{post_id}/publish", response_model=PostRead, dependencies=[Depends(check_api_key)])
def publish_now(post_id: str, db: Session = Depends(get_db)):
    from dawg_agent.services.instagram import publish_reel
    cfg = get_settings()
    if not cfg.publish_enabled:
        raise HTTPException(status_code=403, detail="Publishing safety lock is disabled.")
    post = get_post(db, post_id)
    if not post.approved or not post.media_url:
        raise HTTPException(status_code=409, detail="Post must be approved and uploaded.")
    try:
        media_id = publish_reel(post.media_url, post.caption, cfg)
        post.published_media_id, post.status = media_id, "published"
        db.commit()
        record_event(db, "post.published", post.id, instagram_media_id=media_id)
        db.refresh(post)
        return post
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

@app.get("/events", response_model=list[EventRead], dependencies=[Depends(check_api_key)])
def events(db: Session = Depends(get_db), limit: int = 100):
    limit = max(1, min(limit, 500))
    return list(db.scalars(select(Event).order_by(Event.created_at.desc()).limit(limit)).all())
