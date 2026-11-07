# Troubleshooting

## 1. Python or the `dawg` command is not found

Activate the project environment and install the package:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
dawg --help
```

## 2. FFmpeg or FFprobe is not found

Install FFmpeg, reopen PowerShell, then run `ffmpeg -version` and `ffprobe -version`. The build must include libx264.

## 3. Drive images are not detected

- Confirm Google Drive for desktop is running and the folder is synced locally.
- Confirm `DRIVE_INBOX_DIR` points to the actual local synced folder in `.env`.
- Supported image formats are JPG, JPEG, PNG and WebP.
- Files without a daily publishing slot remain in the incoming folder.

## 4. Image processing fails because audio is missing

Set `AUDIO_SOURCE_PATH` to the exact local campaign audio file. With `AUDIO_REQUIRED=true`, the agent intentionally refuses to render a silent Reel.

## 5. A source image is moved to the failed folder

Check the terminal output and the event log in the local SQLite database. Common causes are a missing/invalid image, missing audio, or FFmpeg/codec errors. Correct the problem and move the image back into the incoming folder for another attempt.

## 6. Instagram publishing fails

The local-file resumable upload requires a Meta app configured for Facebook Login for Business and the appropriate Instagram publishing permissions. Verify:

- Instagram is a professional account and correctly linked to the required Facebook Page.
- The Meta app has the required publishing permissions and access token.
- `INSTAGRAM_USER_ID` and `META_ACCESS_TOKEN` are correct.
- `PUBLISH_ENABLED=true` is set only after configuration is complete.
- The MP4 is valid and the computer is online.

The repository has not been live-tested against your Instagram account. Read the Meta API error carefully; never share access tokens.

## 7. Windows Task Scheduler does not start the agent

Keep the user session signed in, the PC awake and connected to the internet. Ensure Google Drive for desktop has completed sync. Inspect `logs\morning.log`. Only one instance of the worker should run.

## 8. The same image is processed twice

The intake uses a content hash as the post ID. If the source was moved or renamed, identical image bytes still map to the same post. Check the local database before deleting failed records.

## Still stuck?

Share the terminal error and the command you ran. Remove tokens, passwords and private URLs first.
