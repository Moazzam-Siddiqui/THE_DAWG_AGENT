# Start here 👋

This guide assumes you have never run this project before. Follow one step at a time.

## 1. Install Python

Install Python 3.11 or newer.

To check, open PowerShell or a terminal and type:

```bash
python --version
```

You should see something like `Python 3.11.9`.

## 2. Install FFmpeg

FFmpeg is the tool that turns pictures into videos.

After installing it, close and reopen your terminal. Then type:

```bash
ffmpeg -version
```

If you see version information, it is ready.

## 3. Download this project

Open the GitHub repository and choose **Code → Download ZIP**, or use Git:

```bash
git clone https://github.com/Moazzam-Siddiqui/THE_DAWG_AGENT.git
cd THE_DAWG_AGENT
```

## 4. Make a Python playground

This keeps this project's Python packages separate from your other projects.

**Windows PowerShell:**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS or Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 5. Install the project's packages

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## 6. Make your settings file

Copy `.env.example` and name the copy `.env`.

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Do not turn on Instagram publishing. Keep `PUBLISH_ENABLED=false`.

## 7. Make your first video

Put a JPG or PNG dog picture inside `assets/inbox/`.

Open `examples/post.json`. Change `image_path` so it points to your picture. Give the post a new, unique ID.

For example, if your picture is named `my-dog.jpg`:

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

Save this as `my_first_post.json` in the project folder.

Now run:

```bash
dawg render my_first_post.json
```

The video should appear inside `assets/rendered/`.

## 8. Start the control panel

Run:

```bash
uvicorn dawg_agent.api:app --reload
```

Open this address in your browser:

http://127.0.0.1:8000/docs

This is a page where you can try the robot's controls.

## 9. Stop the program

Press `Ctrl + C` in the terminal.

## Remember

Making a video is different from posting a video. This first exercise only makes a video on your computer. It does not publish anything to Instagram.
