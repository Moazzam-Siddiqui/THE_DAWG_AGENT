import json
from pathlib import Path
import typer
from rich import print
from dawg_agent.config import get_settings
from dawg_agent.db import SessionLocal, init_db
from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.queue import approve_post, create_post, render_post

app = typer.Typer(help="THE DAWG AGENT CLI")

@app.command()
def import_manifest(manifest: Path):
    """Import a JSON post manifest as a draft."""
    init_db()
    data = PostCreate.model_validate(json.loads(manifest.read_text(encoding="utf-8")))
    with SessionLocal() as db:
        post = create_post(db, data)
        print(f"[green]Imported draft[/green] {post.id}")

@app.command()
def approve(post_id: str):
    """Approve a queued post."""
    init_db()
    with SessionLocal() as db:
        post = db.get(Post, post_id)
        if not post:
            raise typer.BadParameter("Post not found")
        approve_post(db, post)
        print(f"[green]Approved[/green] {post.id}")

@app.command()
def render(manifest: Path):
    """Import (if needed), approve and render a local preview."""
    init_db()
    data = PostCreate.model_validate(json.loads(manifest.read_text(encoding="utf-8")))
    with SessionLocal() as db:
        post = db.get(Post, data.id) or create_post(db, data)
        if not post.approved:
            approve_post(db, post)
        result = render_post(db, post, get_settings())
        print(f"[green]Rendered[/green] {result.video_path}")

@app.command()
def worker():
    """Run the scheduled publishing worker."""
    from dawg_agent.worker import run_worker
    run_worker()
