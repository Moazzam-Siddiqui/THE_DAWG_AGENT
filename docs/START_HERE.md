# Start here: install and run THE DAWG AGENT

This guide walks through a clean installation on **Windows 10/11**, with macOS and Ubuntu notes where the commands differ. Follow the steps in order. You do not need to install FFmpeg's Python wrapper: this project uses the FFmpeg program installed on your computer.

> **Current scope:** This version can turn a local image into a local MP4 preview and exposes a small API. AI image generation is not connected. Instagram publishing is disabled by default and is not part of the first-run exercise.

## 0. What you need

- Windows 10/11, macOS, or Ubuntu Linux.
- Python **3.11 or newer**.
- FFmpeg and FFprobe.
- Git (recommended; alternatively download the ZIP from GitHub).
- Internet access for installing packages.

## 1. Install Python

### Windows

1. Download Python 3.11 or newer from [python.org/downloads](https://www.python.org/downloads/).
2. Run the installer.
3. On the first installer screen, tick **Add Python to PATH**.
4. Finish installation, then close and reopen PowerShell.

Check the installation:

```powershell
py --version
python --version
```

At least one command should print Python 3.11 or newer. If neither works, rerun the installer and enable **Add Python to PATH**.

### macOS

Install Python 3.11+ from [python.org](https://www.python.org/downloads/macos/) or with Homebrew:

```bash
brew install python@3.12
python3 --version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 --version
```

If the distribution's Python is older than 3.11, install a newer supported Python release before continuing.

## 2. Install FFmpeg (do not skip this)

FFmpeg is the actual video-processing program. Installing the Python packages alone does **not** install FFmpeg. You need the `ffmpeg` and `ffprobe` commands available in your terminal.

### Windows 10/11 — easiest method: WinGet

Open **PowerShell** and run:

```powershell
winget --version
winget install --id Gyan.FFmpeg.Shared --exact
```

Accept the package source terms if Windows asks. When installation finishes:

1. Close **all** PowerShell / Command Prompt windows.
2. Open a new PowerShell window so it loads the updated PATH.
3. Check both tools:

```powershell
ffmpeg -version
ffprobe -version
```

You should see version/build information for both commands. The first line should begin with something similar to `ffmpeg version`.

### Windows alternative: install with Chocolatey

If you already use Chocolatey in an Administrator PowerShell:

```powershell
choco install ffmpeg -y
```

Close and reopen the terminal, then run `ffmpeg -version` and `ffprobe -version`.

### Windows: if the command is still not found

Run:

```powershell
where.exe ffmpeg
where.exe ffprobe
```

If Windows says it cannot find either file, FFmpeg is not on PATH. Find the folder containing `ffmpeg.exe` and `ffprobe.exe` (often a `bin` folder), then add that **bin folder** to your Windows user PATH:

1. Open Start and search **Edit environment variables for your account**.
2. Select **Path** under User variables, then choose **Edit**.
3. Choose **New** and paste the full path to FFmpeg's `bin` folder (not the path to the EXE itself).
4. Save every dialog and reopen PowerShell.
5. Run `where.exe ffmpeg`, `ffmpeg -version`, and `ffprobe -version` again.

### macOS

With Homebrew:

```bash
brew install ffmpeg
ffmpeg -version
ffprobe -version
```

### Ubuntu / Debian

```bash
sudo apt update
sudo apt install -y ffmpeg
ffmpeg -version
ffprobe -version
```

**Do not continue until both FFmpeg commands work.** If you have installed FFmpeg but the terminal cannot find it, fix PATH first.

## 3. Download the project

### Recommended: Git

Install Git from [git-scm.com](https://git-scm.com/downloads) if needed. Open PowerShell or a terminal and run:

```bash
git clone https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT.git
cd THE_DAWG_AGENT
```

### Alternative: ZIP download

Open the [repository](https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT), choose **Code → Download ZIP**, extract it, and open a terminal in the extracted `THE_DAWG_AGENT` folder.

**Important:** Run all project commands from the repository root—the folder containing `pyproject.toml`.

## 4. Create and activate a virtual environment

A virtual environment keeps this project's Python packages separate from other projects.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation with an execution-policy message, use this for the current terminal only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatively, use Command Prompt:

```cmd
py -3.11 -m venv .venv
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When active, your terminal prompt usually starts with `(.venv)`.

## 5. Install THE DAWG AGENT

With the virtual environment active, from the repository root:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

This installs the project and its development tools. The quoted `".[dev]"` form works in PowerShell, Command Prompt, macOS, and Linux.

Check that the command is available:

```bash
dawg --help
```

If your terminal says `dawg` is not recognized, confirm that `.venv` is active and rerun the install command.

## 6. Create your local settings file

Copy the example settings file. Do not commit your real `.env` file or put passwords in GitHub.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux:**

```bash
cp .env.example .env
```

For the first local preview, keep these settings:

```dotenv
PUBLISH_ENABLED=false
REQUIRE_APPROVAL=true
AUDIO_REQUIRED=false
```

You do not need Instagram credentials or Cloudinary credentials to render a local preview. Do not add tokens just to complete this tutorial.

## 7. Create your first video preview

1. Put a JPG or PNG image in `assets/inbox/`.
2. Open `examples/post.json` in a text editor.
3. Change `id` to a unique value and change `image_path` to your image path.
4. Save the file as `my_first_post.json` in the repository root.

Example:

```json
{
  "id": "my-first-dog-video",
  "caption": "Look at this good dog!",
  "hashtags": ["dogs", "dogreels"],
  "image_path": "assets/inbox/my-dog.jpg",
  "audio_path": null,
  "duration_seconds": 9,
  "scheduled_at": null,
  "metadata": {}
}
```

Run:

```bash
dawg render my_first_post.json
```

The CLI renders a **local preview** to `assets/rendered/my-first-dog-video.mp4`. It does not upload or publish anything. This preview command does not add or approve a publishing-queue item.

If you want sound, put an audio file in the project (for example `assets/audio/my-sound.mp3`) and set `audio_path` to that path. If the file is missing, fix the path; do not assume the preview contains sound.

## 8. Run the tests

With the virtual environment still active:

```bash
python -m pytest
```

A passing test run ends with a summary and no failures. Tests do not prove that your Instagram or Cloudinary credentials work; those integrations need separate setup and safe live checks.

## 9. Start the API control panel

In one terminal:

```bash
uvicorn dawg_agent.api:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs). This is the interactive API documentation.

Stop the API with `Ctrl + C`.

To start the scheduler worker, use a **separate terminal** in the project root, activate `.venv`, and run:

```bash
dawg worker
```

The worker checks for scheduled posts. With `PUBLISH_ENABLED=false`, it will not publish. Stop it with `Ctrl + C`.

## 10. Common setup checks

Run these commands from the project root with `.venv` active:

```powershell
python --version
python -m pip --version
dawg --help
ffmpeg -version
ffprobe -version
python -m pytest
```

On macOS/Linux, use `python3` for the system Python check if `python` is unavailable; inside the active virtual environment, `python` should work.

## Before enabling publishing

Do not switch publishing on just because the local preview works. Publishing requires a correctly configured Instagram professional account, Meta app permissions and access token, a publicly reachable video URL, and verified scheduling/rate-limit behavior. Keep `PUBLISH_ENABLED=false` until those pieces have been separately tested.
