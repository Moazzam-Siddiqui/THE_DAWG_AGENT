# How to add a dog post

A post is one picture, one caption, and the settings needed to make a video.

## Step 1: Put the picture in the inbox

Put your dog picture in:

`assets/inbox/`

Example:

`assets/inbox/fluffy.jpg`

## Step 2: Make a small JSON note

Create a file named `fluffy.json`:

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

What do these words mean?

- `id`: A unique name. Do not reuse it for another post.
- `caption`: The words shown with the Reel.
- `hashtags`: A list of hashtags, without the # symbol.
- `image_path`: Where the picture is saved.
- `audio_path`: Where an audio file is saved. Use null for no audio.
- `duration_seconds`: How long the video should be. Use 6 to 12.
- `scheduled_at`: The date and time to publish. Leave null while making a preview.
- `metadata`: Extra notes. The robot does not need these notes to render the video.

## Step 3: Make the video

Run:

```bash
dawg render fluffy.json
```

The video will be saved in `assets/rendered/fluffy-001.mp4`.

## Step 4: Watch it

Open the MP4 file and make sure it looks right.

This command makes a local preview. It does not upload or publish the post.
