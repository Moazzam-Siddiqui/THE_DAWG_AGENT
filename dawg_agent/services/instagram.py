"""Publish a locally rendered Reel directly to Instagram.

Uses Meta's resumable upload flow so the local agent does not need a CDN or
public video URL. This flow requires an app configured for Facebook Login
for Business and the corresponding Instagram publishing permissions.
"""
import time
from pathlib import Path

import httpx

from dawg_agent.config import Settings


class InstagramPublishError(RuntimeError):
    """Instagram could not publish the Reel."""


def publish_reel(video_path: str | Path, caption: str, settings: Settings) -> str:
    """Upload a local MP4 to Meta, wait for processing, then publish it."""
    video = Path(video_path)
    if not settings.publish_enabled:
        raise InstagramPublishError("Publishing is OFF in the settings.")
    if not settings.instagram_is_ready:
        raise InstagramPublishError(
            "Add INSTAGRAM_USER_ID and META_ACCESS_TOKEN to the .env file."
        )
    if not video.is_file():
        raise InstagramPublishError(f"Rendered video does not exist: {video}")

    graph = f"https://graph.facebook.com/{settings.meta_graph_version}"
    headers = {"Authorization": f"Bearer {settings.meta_access_token}"}

    try:
        # Create a resumable media container. This avoids Cloudinary/public URLs.
        create = httpx.post(
            f"{graph}/{settings.instagram_user_id}/media",
            data={
                "media_type": "REELS",
                "upload_type": "resumable",
                "caption": caption,
                "share_to_feed": "true",
            },
            headers=headers,
            timeout=60,
        )
        create.raise_for_status()
        payload = create.json()
        container_id = payload.get("id")
        upload_uri = payload.get("uri")
        if not container_id or not upload_uri:
            raise InstagramPublishError(
                "Meta did not return both a media container ID and upload URI."
            )

        file_size = video.stat().st_size
        with video.open("rb") as media:
            upload = httpx.post(
                upload_uri,
                content=media,
                headers={
                    "Authorization": f"OAuth {settings.meta_access_token}",
                    "offset": "0",
                    "file_size": str(file_size),
                    "Content-Type": "application/octet-stream",
                },
                timeout=300,
            )
        upload.raise_for_status()
        if upload.json().get("success") is not True:
            raise InstagramPublishError("Meta did not confirm the video upload.")

        # Instagram must finish processing before the publish request.
        status_code = None
        for _attempt in range(settings.instagram_processing_attempts):
            status = httpx.get(
                f"{graph}/{container_id}",
                params={"fields": "status_code"},
                headers=headers,
                timeout=30,
            )
            status.raise_for_status()
            status_code = status.json().get("status_code")
            if status_code == "FINISHED":
                break
            if status_code in {"ERROR", "EXPIRED"}:
                raise InstagramPublishError(
                    f"Instagram rejected the video during processing: {status_code}"
                )
            time.sleep(settings.instagram_processing_poll_seconds)

        if status_code != "FINISHED":
            raise InstagramPublishError("Instagram video processing timed out.")

        publish = httpx.post(
            f"{graph}/{settings.instagram_user_id}/media_publish",
            data={"creation_id": container_id},
            headers=headers,
            timeout=60,
        )
        publish.raise_for_status()
        media_id = publish.json().get("id")
        if not media_id:
            raise InstagramPublishError("Instagram did not return a published media ID.")
        return media_id

    except httpx.HTTPError as error:
        raise InstagramPublishError(f"Instagram API request failed: {error}") from error
