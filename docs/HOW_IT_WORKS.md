# How THE DAWG AGENT works

## The mental model

**ChatGPT makes the image → Drive hands it over → your PC makes the Reel → Instagram publishes it.**

ChatGPT remains the only image generator in this campaign. This repository does not call an image-generation API or local image model.

## Pipeline

1. Save a ChatGPT-generated image into the Google Drive for desktop synced incoming folder.
2. The morning command finds supported JPG, JPEG, PNG and WebP images.
3. It creates a stable content hash, preventing the same image from being ingested twice.
4. FFmpeg renders a 1080×1920 vertical MP4 and adds the configured campaign audio.
5. The renderer checks that the video exists, has the expected dimensions, and contains audio.
6. SQLite records the post and scheduled time.
7. The worker uploads the local MP4 bytes directly to Meta using Instagram's resumable upload flow.
8. The worker waits for Instagram processing and publishes only after Meta reports FINISHED.
9. Events and failures are recorded locally.

## Local folders

| Folder | Purpose |
|---|---|
| Google Drive `01_INCOMING_IMAGES` | Drop ChatGPT-generated images here |
| Google Drive `04_PROCESSED_IMAGES` | Source images already ingested |
| Google Drive `05_FAILED_IMAGES` | Source images that failed processing |
| `assets/rendered` | Finished local MP4 files |
| `data/dawg_agent.db` | Local SQLite queue and event log |
| `assets/audio` | User-supplied campaign audio |

Google Drive for desktop is the sync mechanism. The Python agent reads the synced local folder; no Google Drive API or Cloudinary account is used.

## Commands

- `dawg morning`: ingest Drive images, render, validate and schedule.
- `dawg worker`: keep the Instagram publishing worker running.
- `dawg run`: run morning intake once, then start the worker.
- `dawg render post.json`: render one local preview.

## Direct Instagram upload

The Instagram adapter uses Meta's resumable upload flow. It creates a Reel container, uploads the local MP4 to the returned Meta upload URI, polls the container status, and publishes it. This avoids a public CDN/video URL.

Meta resumable upload has a specific app-login requirement: Facebook Login for Business. The Meta app, Instagram professional account, Page linkage, access token and publishing permissions must be configured before this can work. No live account test has been performed yet.

## Automatic mode

The Drive intake marks a post approved after it passes local validation. This is the requested automatic mode. Publishing itself remains globally disabled until `PUBLISH_ENABLED=true` is set deliberately.

Default limits: 3 posts/day, 180-minute minimum interval, 07:00–22:00 Asia/Kolkata. Only one worker instance should run because atomic cross-process claiming and guaranteed duplicate-publish recovery are not yet implemented.

## Honest limitations

- ChatGPT does not automatically save images into Drive through this repository. The image must be saved into the synced incoming folder.
- Captions are currently a fixed configurable caption and hashtags, not AI-generated roasts.
- Audio is included from a configured local file; the program cannot independently identify or verify that it is the exact "What da dog doin" recording.
- Instagram publishing needs a live controlled test with your Meta app/account.
- The local PC must stay awake, online and signed in for scheduled work.
