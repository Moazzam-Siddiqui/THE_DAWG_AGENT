# Start THE DAWG AGENT on Windows

This is a Windows-first local pipeline. ChatGPT creates the images; Google Drive for desktop syncs them; your PC renders and publishes the Reels.

## Requirements

- Windows 10/11
- Python 3.11+
- FFmpeg and FFprobe on PATH
- Google Drive for desktop
- A Meta app configured for Instagram publishing via Facebook Login for Business
- The campaign audio file supplied by you

## Install

```powershell
git clone https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT.git
cd THE_DAWG_AGENT
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Check the tools:

```powershell
python --version
ffmpeg -version
ffprobe -version
dawg --help
```

## Connect the Drive handoff

In Google Drive for desktop, create a synced folder such as:

```text
G:\My Drive\THE_DAWG_CAMPAIGN\01_INCOMING_IMAGES
G:\My Drive\THE_DAWG_CAMPAIGN\04_PROCESSED_IMAGES
G:\My Drive\THE_DAWG_CAMPAIGN\05_FAILED_IMAGES
```

Set the three matching `DRIVE_..._DIR` values in `.env` to the real local paths. The agent reads the synced local folder; it does not use a Google Drive API integration.

Generate images with ChatGPT and save each image into `01_INCOMING_IMAGES`. The repository cannot currently make ChatGPT automatically save its generated images into Drive.

## Add the campaign audio

Place the exact "What da dog doin" audio file at the configured `AUDIO_SOURCE_PATH`. The default is:

```text
assets/audio/what_da_dog_doing.mp3
```

If the file is absent, the morning intake will fail the affected image rather than render a silent Reel.

## Configure Instagram

Set `INSTAGRAM_USER_ID` and `META_ACCESS_TOKEN` in `.env`. The current direct local-file upload uses Meta's resumable Instagram Reel upload route. Meta documents this route for apps using Facebook Login for Business; use the required account linkage and content-publishing permissions.

Keep `PUBLISH_ENABLED=false` for the first render test. After the Meta app, professional account, token and permissions are verified, change it to `true`.

## Run the pipeline

Run intake once:

```powershell
dawg morning
```

Start the scheduler:

```powershell
dawg worker
```

Or run both in one process:

```powershell
dawg run
```

## Run automatically every morning

From the repository root, register the Windows Task Scheduler job:

```powershell
.\scripts\install_task.ps1
```

It starts at 06:00 as your current Windows user. Keep the PC awake, online, signed in, and Google Drive synced. The script performs the morning intake and keeps the publishing worker running. Only one worker should run.

To remove the scheduled task:

```powershell
Unregister-ScheduledTask -TaskName "TheDawgAgentMorning" -Confirm:$false
```

## Tests

```powershell
python -m pytest
```

A green test suite checks local logic only; it does not prove Meta account permissions or live publishing.
