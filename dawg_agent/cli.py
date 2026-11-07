"""Commands you can type to tell the robot what to do."""
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

app = typer.Typer(help="Simple commands for THE DAWG AGENT.")


def read_post_file(file_path: Path) -> PostCreate:
    """Read a JSON post file and check that it has the right information."""
    try:
        file_contents = file_path.read_text(encoding="utf-8")
        return PostCreate.model_validate(json.loads(file_contents))
    except FileNotFoundError as error:
        raise typer.BadParameter(f"I cannot find the file: {file_path}") from error
    except (json.JSONDecodeError, ValueError) as error:
        raise typer.BadParameter(f"The post file has a problem: {error}") from error


@app.command()
def import_post(file_path: Path):
    """Add a JSON post file to the waiting list."""
    init_db()
    post_details = read_post_file(file_path)

    with SessionLocal() as database:
        post = create_post(database, post_details)
        print(f"[green]Added post:[/green] {post.id}")


@app.command()
def approve(post_id: str):
    """Approve a post so the robot can work on it."""
    init_db()

    with SessionLocal() as database:
        post = database.get(Post, post_id)
        if post is None:
            raise typer.BadParameter("I cannot find that post ID.")

        approve_post(database, post)
        print(f"[green]Approved:[/green] {post.id}")


@app.command()
def render(file_path: Path):
    """Render a local preview without creating or approving a queue item."""
    post_details = read_post_file(file_path)
    settings = get_settings()
    output_path = settings.output_dir / f"{post_details.id}.mp4"

    audio_path = post_details.audio_path or settings.audio_source_path
    render_reel(
        image_path=post_details.image_path,
        output_path=output_path,
        duration=post_details.duration_seconds,
        settings=settings,
        audio_path=audio_path,
    )

    print(f"[green]Video preview saved to:[/green] {output_path}")


@app.command()
def worker():
    """Start the clock-watching worker."""
    from dawg_agent.worker import run_worker

    run_worker()
