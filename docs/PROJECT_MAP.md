# Project map

```text
THE_DAWG_AGENT/
|-- dawg_agent/
|   |-- api.py                 Local control API
|   |-- cli.py                 dawg morning / worker / run commands
|   |-- config.py              Local .env settings
|   |-- db.py                  SQLite connection
|   |-- models.py              Post and event records
|   |-- worker.py              Scheduled Instagram publisher
|   |-- services/
|       |-- drive_intake.py    Reads Google Drive desktop synced images
|       |-- instagram.py       Meta resumable upload from local MP4
|       |-- publishing.py      Publishing window and rate limits
|       |-- queue.py           Post state transitions
|       |-- render.py          FFmpeg video rendering and checks
|       |-- events.py          Local activity log
|-- assets/
|   |-- audio/                 User-supplied campaign sound
|   |-- rendered/              Finished MP4 files
|-- drive/                     Default Drive-sync inbox/archive folders
|-- scripts/
|   |-- run_morning.bat        Windows launcher
|   |-- install_task.ps1       Register daily Task Scheduler job
|-- docs/
|-- tests/
|-- .env.example
|-- pyproject.toml
```

## Data path

ChatGPT image → Google Drive for desktop synced folder → local intake → FFmpeg + supplied audio → SQLite schedule → Meta resumable upload → Instagram.
