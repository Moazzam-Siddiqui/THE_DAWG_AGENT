# Troubleshooting

Start with the exact error message. Most setup problems come from the terminal using the wrong Python environment, FFmpeg not being on PATH, or running a command outside the project folder.

## 1. Windows says `python`, `py`, or `pip` is not recognized

- Reinstall Python 3.11+ from [python.org](https://www.python.org/downloads/).
- Tick **Add Python to PATH** during installation.
- Close and reopen PowerShell.
- Check with `py --version` and `python --version`.
- Prefer `python -m pip` over bare `pip` so packages install into the Python you selected.

## 2. PowerShell says script execution is disabled

Run this in the current PowerShell window:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for that terminal process. Or use Command Prompt and run `.venv\Scripts\activate.bat`.

## 3. `ffmpeg` or `ffprobe` is not recognized

Installing Python dependencies does not install FFmpeg.

On Windows, install it with:

```powershell
winget install --id Gyan.FFmpeg.Shared --exact
```

Close and reopen PowerShell, then verify:

```powershell
where.exe ffmpeg
where.exe ffprobe
ffmpeg -version
ffprobe -version
```

If `where.exe` finds nothing, add the folder containing `ffmpeg.exe` and `ffprobe.exe` (usually its `bin` folder) to your Windows user PATH. See [Start here — Install FFmpeg](START_HERE.md#2-install-ffmpeg-do-not-skip-this).

On macOS use `brew install ffmpeg`. On Ubuntu/Debian use `sudo apt update && sudo apt install -y ffmpeg`.

## 4. `No module named dawg_agent` or `dawg` is not recognized

Make sure:
1. Your terminal is in the repository root (the folder containing `pyproject.toml`).
2. The virtual environment is active; the prompt should show `(.venv)`.
3. You installed the project with:

```bash
python -m pip install -e ".[dev]"
```

If you opened a new terminal, activate the environment again before running project commands.

## 5. `No such file or directory` when rendering

- Confirm the image exists.
- Check the spelling and file extension.
- Use a path relative to the repository root, such as `assets/inbox/my-dog.jpg`.
- Make sure you run the command from the repository root.
- Confirm the image is a valid JPG or PNG that Pillow can open.

## 6. `The post ID is already being used`

The database already contains that ID. Choose a new unique `id` in your JSON file. For a local preview, the CLI does not need to create a queue record, but the ID still determines the output MP4 filename.

## 7. The video has no sound

- `"audio_path": null` deliberately creates a silent video.
- If you supplied a path, confirm that the audio file exists at that exact path.
- The current renderer uses one audio file. It does not mix voiceover, music, and sound effects as separate tracks.
- Only use audio you own or have permission to use.

## 8. FFmpeg reports an encoder or codec error

Check that the FFmpeg installation includes the H.264 encoder used by this project:

```bash
ffmpeg -hide_banner -encoders
```

Look for `libx264`. If it is missing, install a full FFmpeg build that includes libx264, then restart your terminal and try again.

## 9. The API does not start

- Confirm the virtual environment is active and dependencies are installed.
- Check whether another program is already using port 8000.
- Run `uvicorn dawg_agent.api:app --reload` from the repository root.
- Read the first traceback in the terminal; do not share secrets from `.env`.

## 10. Instagram publishing does not work

A local video preview does not prove Instagram publishing is configured. Check the professional account, linked Facebook Page, Meta app permissions, token validity, Cloudinary public URL, and Meta API response. Keep `PUBLISH_ENABLED=false` until you have deliberately tested the complete flow. Never paste access tokens into GitHub issues or chat.

## Still stuck?

Share the complete terminal error and the command you ran. Remove access tokens, API keys, passwords, and private URLs first. Include your operating system and the output of `python --version`, `ffmpeg -version`, and `ffprobe -version`.
