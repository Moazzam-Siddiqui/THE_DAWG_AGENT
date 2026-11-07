# THE DAWG AGENT

An automation-first content pipeline for `@what_the_dawg_doing_6969`.

It turns approved dog-image assets into vertical Reel videos, validates the output, stages artifacts, and (when explicitly enabled and configured) publishes through Instagram's official Graph API.

## Current status

This repository contains the first runnable implementation:
- JSON content queue with explicit lifecycle states
- FFmpeg 9:16 Reel renderer with optional supplied audio
- Media validation (dimensions, duration, audio policy)
- Cloudinary upload adapter (unsigned upload preset supported)
- Instagram Graph API publishing adapter
- APScheduler-based due-post worker
- FastAPI control plane and health/status endpoints
- SQLite persistence, idempotency keys, retries, and audit events
- Safe defaults: publishing is disabled; queued posts require approval

**No posts are published by default.** The scheduler will only act on approved items and publishing requires `PUBLISH_ENABLED=true` plus valid credentials.

## Architecture

```
assets/inbox/  ->  queue JSON  ->  renderer (FFmpeg)  ->  QA
                                              |
                                              v
                                       Cloudinary URL
                                              |
                                approved + due + enabled?
                                              |
                                              v
                                     Instagram Graph API
```

GitHub is used for source, queue manifests, captions, and lightweight metadata. Do not commit generated videos, secrets, or large image binaries to Git history. Put media in object storage (Cloudinary) and keep only its URL and checksum in the queue manifest.

## Quick start

Requirements: Python 3.11+, FFmpeg installed and available on PATH.

1. Create an environment and install dependencies:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

2. Copy `.env.example` to `.env` and adjust local paths. Keep publishing disabled initially.

3. Add an image to `assets/inbox/`, then copy `examples/post.json` to `queue/inbox/<your-id>.json` and edit its `image_path`.

4. Run a preview:

```bash
dawg render queue/inbox/<your-id>.json
```

5. Start the API and worker:

```bash
uvicorn dawg_agent.api:app --reload
dawg worker
```

Open `http://127.0.0.1:8000/docs`.

## Queue lifecycle

`draft -> approved -> rendered -> uploaded -> scheduled -> published`

Failure states are recorded with a retryable error. Approval is a required gate. The API's approve route records an explicit approval event.

## Configuration

See `.env.example`. Important settings:
- `PUBLISH_ENABLED=false`: safety lock; must be explicitly changed to enable publishing.
- `MAX_POSTS_PER_DAY=3`: conservative default; set in accordance with Meta limits and account health.
- `MIN_POST_INTERVAL_MINUTES=180`: prevents burst posting.
- `TIMEZONE=Asia/Kolkata`.
- Cloudinary: `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_UPLOAD_PRESET`.
- Instagram: `INSTAGRAM_USER_ID`, `META_ACCESS_TOKEN`, `META_GRAPH_VERSION`.

Use a long-lived, appropriately permissioned Meta token and a professional Instagram account connected to a Facebook Page. Follow Meta's current platform terms and publishing limits.

## API

- `GET /health` — service health
- `GET /posts` — list queue items
- `POST /posts` — create a draft
- `POST /posts/{id}/approve` — approve
- `POST /posts/{id}/render` — render and validate
- `POST /posts/{id}/upload` — upload rendered media
- `POST /posts/{id}/schedule` — set publish time
- `POST /posts/{id}/publish` — publish now (requires safety lock off)
- `GET /events` — audit trail

The endpoints that cause external side effects are disabled unless publishing configuration is complete.

## Dog content brief

The default content brief is in `config/content_brief.md`. It favors varied, original dog scenes, concise comedy, and clearly satirical commentary. Avoid deceptive claims, impersonation, fake engagement, or repetitive spam. The word "sissy" is retained as a required comedic roast token in the configured satire format, but avoid directing abuse at private individuals.

## Tests

```bash
pytest
```

## License

MIT
