# Windows morning automation

## 1. Configure the folders

Install Google Drive for desktop and make sure the campaign folder is available offline / synced locally. Example:

```text
G:\My Drive\THE_DAWG_CAMPAIGN\
  01_INCOMING_IMAGES\
  04_PROCESSED_IMAGES\
  05_FAILED_IMAGES\
```

Set the three `DRIVE_*_DIR` values in `.env` to those exact paths. Save ChatGPT-generated images in `01_INCOMING_IMAGES`.

## 2. Configure audio

Put the campaign's permitted audio file at the path in `AUDIO_SOURCE_PATH`. The morning intake fails an image if required audio is missing; it does not silently create a silent Reel.

## 3. Create the launcher

From the repository root, double-clicking `scripts\run_morning.bat` is a manual test. It runs `dawg morning`, then keeps the publishing worker running.

## 4. Register the daily task

Open PowerShell in the repository root and run:

```powershell
.\scripts\install_task.ps1
```

The task is configured to start at 06:00 every day and run as the current Windows user. The computer must be awake, signed in, online, and Google Drive must be synced. Do not create multiple copies of the task or run multiple workers.

To remove it:

```powershell
Unregister-ScheduledTask -TaskName "TheDawgAgentMorning" -Confirm:$false
```

## 5. Keep publishing disabled until ready

The sample `.env` intentionally uses `PUBLISH_ENABLED=false`. Configure Meta's app and Instagram professional account, run a local render test, then enable publishing only after a controlled test. The script does not turn publishing on by itself.
