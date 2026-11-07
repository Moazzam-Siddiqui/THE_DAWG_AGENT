# THE DAWG AGENT

Approval-gated dog Reel production and publishing pipeline for @what_the_dawg_doing_6969.

Features: JSON queue, SQLite lifecycle, FFmpeg 9:16 rendering, media validation, Cloudinary upload, Instagram Graph API publishing, FastAPI control plane, APScheduler worker, idempotency, retries, audit trail.

GitHub stores source, prompts, manifests, and metadata. Store large media in Cloudinary/object storage, not Git history.

## Local start
Requires Python 3.11+ and FFmpeg on PATH.
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
```
Copy .env.example to .env. Keep PUBLISH_ENABLED=false until Meta permissions and credentials are verified. Place an image in assets/inbox/, then adapt examples/post.json.
```bash
dawg render examples/post.json
uvicorn dawg_agent.api:app --reload
dawg worker
```
API docs: http://127.0.0.1:8000/docs

Lifecycle: draft -> approved -> rendered -> uploaded -> scheduled -> published. Approval is required. Publishing is disabled by default.

Default rate controls: 3 posts/day, 180 minutes between posts, 07:00–22:00 Asia/Kolkata. Follow current Meta limits and account health. No fake engagement, deceptive impersonation, threats, doxxing, or automated harassment.

See config/content_brief.md. Never commit credentials or generated videos. Run tests with pytest.
