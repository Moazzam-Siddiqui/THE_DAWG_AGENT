# THE DAWG AGENT 🐶

**A Windows-first, local production agent that turns ChatGPT-generated dog images into Instagram Reels.**

ChatGPT remains the image generator. Google Drive for desktop is the handoff folder. The local agent renders and validates videos with FFmpeg, adds the supplied campaign audio, stores everything on disk, and publishes directly to Instagram through Meta's resumable upload API. No Cloudinary or external video CDN is used.

> **Important handoff limitation:** ChatGPT image generation does not automatically write files into your Google Drive from this repository. Save each generated image into the Drive-synced `01_INCOMING_IMAGES` folder. The local agent takes over from there. Do not substitute another image generator.

> **Project status:** Local intake, rendering, queueing and direct-upload code are being built. Instagram publishing still requires a correctly configured Meta app/account and a live end-to-end verification. Publishing is OFF by default.

> **License:** Personal, non-commercial, limited customization. See [LICENSE](LICENSE).

## The pipeline

```text
ChatGPT image generation
        |
        v
Google Drive for desktop (synced folder)
        |
        v
Windows morning task
        |
        v
Local Python agent + SQLite
        |
        +--> FFmpeg vertical Reel + supplied audio
        |
        +--> Local video validation
        |
        v
Daily publishing queue
        |
        v
Meta Instagram resumable upload (local MP4 bytes)
        |
        v
Instagram Reel
```

## What is local

- Images, source audio, rendered MP4s, SQLite database, queue and logs stay on your PC / Google Drive sync.
- FFmpeg handles video rendering.
- Meta's resumable upload flow sends the local MP4 directly to Instagram; no public CDN URL is required.
- Google Drive for desktop performs folder synchronization. This project does not call the Google Drive API.

## Windows setup

1. Install Python 3.11+, Git, FFmpeg and Google Drive for desktop.
2. Clone the repository and install it:

```powershell
git clone https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT.git
cd THE_DAWG_AGENT
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

3. In Google Drive for desktop, choose a local synced folder, for example:
   `G:\My Drive\THE_DAWG_CAMPAIGN\01_INCOMING_IMAGES`.
4. Set `DRIVE_INBOX_DIR`, `DRIVE_PROCESSED_DIR`, and `DRIVE_FAILED_DIR` in `.env` to folders inside that synced Drive directory.
5. Put your user-supplied "What da dog doin" audio at `assets/audio/what_da_dog_doing.mp3`, or change `AUDIO_SOURCE_PATH`.
6. Configure the Meta Instagram professional account and access token (see below). Keep publishing disabled while testing.

## Daily operation

Save ChatGPT-generated images into the Drive-synced incoming folder. Then run:

```powershell
dawg morning
```

This imports new images, checks for the required audio, renders a 9:16 MP4, validates it, and schedules up to the daily cap. Files without a slot remain in the incoming folder for a later run. Processed and failed images are moved into their corresponding Drive folders.

Start the publisher:

```powershell
dawg worker
```

Or use the combined command:

```powershell
dawg run
```

The included `scripts\run_morning.bat` is intended for Windows Task Scheduler. It runs the morning intake and keeps the scheduler alive. See [docs/WINDOWS_AUTOMATION.md](docs/WINDOWS_AUTOMATION.md).

## Instagram setup

The local-file resumable upload flow uses Meta's Instagram Graph API. Configure:

- `INSTAGRAM_USER_ID`
- `META_ACCESS_TOKEN`
- `META_GRAPH_VERSION`

Meta's documented resumable upload route requires an app configured for **Facebook Login for Business** and the appropriate Instagram publishing permissions. A professional Instagram account and the required Page/app setup are also necessary. This is not an Instagram password login and does not bypass Meta permissions.

The code creates a Reel container, uploads the local MP4 bytes to the returned Meta upload URI, waits for processing to finish, and then publishes the container. This flow has not yet been live-tested against your account.

## Automatic publishing and safety

- `REQUIRE_APPROVAL=false`: successfully rendered Drive intake is automatically approved.
- `PUBLISH_ENABLED=false`: hard stop until you deliberately enable publishing after Meta setup.
- Default cap: 3 posts per local day.
- Default spacing: at least 180 minutes between published posts.
- Publishing window: 07:00–22:00 Asia/Kolkata.
- Only rendered, scheduled posts can reach the publishing worker.

Do not turn publishing on until the Meta app and account have been configured and a controlled test has succeeded. The local machine must be awake, online, signed in, and able to access the Drive-synced folder at the scheduled times.

## Checks

```powershell
ffmpeg -version
ffprobe -version
dawg --help
python -m pytest
```

## Current limitations

- ChatGPT image generation is not callable automatically from this local repository. The image-to-Drive handoff is currently saving the generated image into the synced incoming folder.
- Caption generation is currently a configured template, not an LLM-generated roast writer.
- The agent does not verify that an audio file is the exact campaign sound; it checks that the configured audio file exists and is included.
- The Meta resumable upload flow requires Facebook Login for Business; account/app permissions and live publication remain to be verified.
- No production-grade cross-process publish lock or guaranteed duplicate recovery yet. Run one worker instance only.

See [How it works](docs/HOW_IT_WORKS.md) and [Windows automation](docs/WINDOWS_AUTOMATION.md).
