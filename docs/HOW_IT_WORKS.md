# How THE DAWG AGENT works

THE DAWG AGENT is currently an early-stage, approval-gated media workflow. It has a local image-to-video renderer, a database-backed post queue, an API, Cloudinary upload code, an Instagram publishing adapter, and a scheduler worker. Some integrations still require credentials and real-environment verification.

## The intended production journey

```text
CREATIVE BRIEF
     |
     v
IMAGE + AUDIO ASSETS
     |
     v
POST DRAFT / QUEUE
     |
     v
HUMAN APPROVAL
     |
     v
VIDEO RENDER + VALIDATION
     |
     v
CLOUDINARY UPLOAD
     |
     v
SCHEDULED QUEUE
     |
     v
INSTAGRAM PUBLISHING
     |
     v
EVENT LOG / MONITORING
```

**Important distinction:** AI image generation and automatic prompt generation are not connected in the current code. The current renderer starts with an image file supplied by a person.

## What each part does

| Part | File | Responsibility |
|---|---|---|
| Settings | `config.py` | Reads environment variables and safe defaults |
| Database | `db.py`, `models.py` | Stores posts and events |
| Input validation | `schemas.py` | Checks incoming post/API data |
| Queue | `services/queue.py` | Creates posts and moves them through workflow states |
| Rendering | `services/render.py` | Uses FFmpeg to make and inspect a vertical MP4 |
| Cloud storage | `services/cloudinary.py` | Uploads a rendered MP4 and returns its URL |
| Instagram | `services/instagram.py` | Calls the Meta Graph API to create and publish a Reel |
| API | `api.py` | Provides HTTP endpoints to control the workflow |
| CLI | `cli.py` | Provides terminal commands |
| Worker | `worker.py` | Checks scheduled posts and attempts publication |
| Events | `services/events.py` | Records workflow events |

## Queue states

| Status | Meaning |
|---|---|
| `draft` | Post details have been saved |
| `approved` | A person approved the post |
| `rendered` | An MP4 was created |
| `uploaded` | The MP4 has a Cloudinary URL |
| `scheduled` | A future publishing time has been saved |
| `published` | Instagram returned a media ID |
| `failed` | The worker exhausted its configured retries |

The local `dawg render` command is a preview shortcut. It does not create or approve a queue record. Queue operations are separate.

## API and worker

Start the API from the repository root with:

```bash
uvicorn dawg_agent.api:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to inspect the available endpoints.

Start the scheduler in a second terminal:

```bash
dawg worker
```

The worker checks for due scheduled posts. It will not publish while `PUBLISH_ENABLED=false`.

## Safety and current limitations

- Publishing is disabled by default.
- Human approval is required by default for queue rendering and upload.
- A local preview is not an approval to publish.
- The worker has configured daily limits and a publishing time window, but those controls still need stronger tests and hardening before live use.
- The API's immediate-publish endpoint is a separate path; do not expose it publicly or enable publishing until it is hardened.
- AI prompt generation, image generation, multi-track audio mixing, a visual dashboard, and deployment automation are not implemented yet.

Treat this as an engineering project under active development, not a production autopublisher.
