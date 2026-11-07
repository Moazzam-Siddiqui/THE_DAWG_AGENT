# Add a post to the local pipeline

The main campaign flow uses the Google Drive synced inbox. Save a ChatGPT-generated image into the configured `DRIVE_INBOX_DIR`, then run:

```powershell
dawg morning
```

The local agent assigns a stable ID, adds the configured campaign audio, renders and validates an MP4, then places the post into the automatic publishing queue. Excess images remain in the inbox for the next daily run.

For an isolated local preview, you can still create a JSON file:

```json
{
  "id": "dog-preview-001",
  "caption": "What da dog doin? 🐶",
  "hashtags": ["dogs", "dogreels"],
  "image_path": "assets/inbox/dog.jpg",
  "audio_path": "assets/audio/what_da_dog_doing.mp3",
  "duration_seconds": 9,
  "scheduled_at": null,
  "metadata": {}
}
```

Then run:

```powershell
dawg render dog-preview.json
```

The preview is saved under `assets/rendered/`. It is not uploaded or published.

The local pipeline uses one supplied audio file. It does not identify or download Instagram audio. Use only an audio file you own or have permission to use.
