"""Commands for THE DAWG AGENT."""
import json
from pathlib import Path

import typer
from rich import print

from dawg_agent.config import get_settings
from dawg_agent.db import SessionLocal, init_db
from dawg_agent.models import Post
from dawg_agent.schemas import PostCreate
from dawg_agent.services.queue import approve_post, create_post
from dawg_agent.services.render import render_reel

app = typer.Typer(help="Local-first commands for THE DAWG AGENT.")


def read_post_file(file_path: Path) -> PostCreate:
    try:
        return PostCreate.model_validate(json.loads(file_path.read_text(encoding="utf-8")))
    except FileNotFoundError as error:
        raise typer.BadParameter(f"I cannot find the file: {file_path}") from error
    except (json.JSONDecodeError, ValueError) as error:
        raise typer.BadParameter(f"The post file has a problem: {error}") from error


@app.command()
def import_post(file_path: Path):
    """Add a JSON post file to the queue."""
    init_db()
    with SessionLocal() as database:
        post = create_post(database, read_post_file(file_path))
        print(f"[green]Added post:[/green] {post.id}")


@app.command()
def approve(post_id: str):
    """Approve a queued post."""
    init_db()
    with SessionLocal() as database:
        post = database.get(Post, post_id)
        if post is None:
            raise typer.BadParameter("I cannot find that post ID.")
        approve_post(database, post)
        print(f"[green]Approved:[/green] {post.id}")


@app.command()
def render(file_path: Path):
    """Render a local preview without creating a queue item."""
    details = read_post_file(file_path)
    settings = get_settings()
    output = settings.output_dir / f"{details.id}.mp4"
    render_reel(details.image_path, output, details.duration_seconds, settings,
                details.audio_path or settings.audio_source_path)
    print(f"[green]Video preview saved to:[/green] {output}")


@app.command()
def morning():
    """Process new ChatGPT images from the Google Drive synced inbox."""
    init_db()
    settings = get_settings()
    from dawg_agent.services.drive_intake import ingest_drive_images
    with SessionLocal() as database:
        result = ingest_drive_images(database, settings)
    print("[bold]Morning run complete[/bold]")
    for key, value in result.items():
        print(f"{key}: {value}")


@app.command()
def worker():
    """Start the Instagram publishing scheduler."""
    from dawg_agent.worker import run_worker
    run_worker()


@app.command()
def run():
    """Process the Drive inbox once, then keep the publishing worker running."""
    morning()
    worker()
