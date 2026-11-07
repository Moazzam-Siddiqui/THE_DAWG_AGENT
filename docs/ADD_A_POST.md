# How to add a dog post

This guide explains how to prepare a JSON post file and render a local MP4 preview.

> A local preview is not an Instagram post. It does not upload, schedule, or publish anything.

## 1. Add your image

Put a valid JPG or PNG in:

```text
assets/inbox/
```

Example: `assets/inbox/fluffy.jpg`.

Run commands from the repository root so relative paths resolve correctly.

## 2. Create a post JSON file

Create `fluffy.json` in the repository root:

```json
{
  "id": "fluffy-001",
  "caption": "Fluffy has entered the room.",
  "hashtags": ["dog", "funnydog"],
  "image_path": "assets/inbox/fluffy.jpg",
  "audio_path": null,
  "duration_seconds": 9,
  "scheduled_at": null,
  "metadata": {
    "idea": "Fluffy looks surprised"
  }
}
```

### What each field means

| Field | Meaning |
|---|---|
| `id` | Unique identifier; also used for the output filename |
| `caption` | Caption text |
| `hashtags` | Hashtags without the `#` symbol |
| `image_path` | Input image path, relative to the project root or an absolute path |
| `audio_path` | Audio file path, or `null` for silent output |
| `duration_seconds` | Video duration; between 6 and 12 seconds |
| `scheduled_at` | Optional timezone-aware date/time for queue scheduling; leave null for a preview |
| `metadata` | Extra notes saved with a queued post; not used by the current renderer |

The current renderer uses one audio file. It does not yet mix multiple tracks or select sounds automatically.

## 3. Render a local preview

Activate your virtual environment, make sure FFmpeg is installed, and run:

```bash
dawg render fluffy.json
```

Expected output location:

```text
assets/rendered/fluffy-001.mp4
```

The CLI preview renders directly from the JSON file. It does not create a database queue entry, upload the file, or approve/publish anything.

## 4. Check the result

Open the MP4 and inspect:
- The image is framed correctly in vertical 9:16.
- The dog is visible and not cropped badly.
- The duration is what you expected.
- Audio is present only if you supplied a valid audio file.
- The video plays from beginning to end.

You can inspect the file's technical details with:

```bash
ffprobe -hide_banner assets/rendered/fluffy-001.mp4
```

## 5. Importing a post into the API queue

The CLI also has an import command:

```bash
dawg import-post fluffy.json
```

This stores a draft in the local database. It does not render, upload, or publish it. The API exposes approval, rendering, uploading, and scheduling endpoints; see [the API docs](http://127.0.0.1:8000/docs) after starting the API.

## 6. Change the sound

Put the sound file in your project, for example `assets/audio/fluffy.mp3`, and change:

```json
"audio_path": "assets/audio/fluffy.mp3"
```

For a silent video:

```json
"audio_path": null
```

Use only audio you own or have permission to use. See [Customize prompts, post types, and audio](CUSTOMIZE_PROMPTS.md) for creative guidance and current feature limitations.
