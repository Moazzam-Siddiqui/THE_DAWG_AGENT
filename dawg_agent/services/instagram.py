"""Publish a Reel using Instagram's official Graph API."""
import time

import httpx

from dawg_agent.config import Settings


class InstagramPublishError(RuntimeError):
    """Instagram could not publish the Reel."""


def publish_reel(video_link: str, caption: str, settings: Settings) -> str:
    """Give Instagram a video link and ask it to publish a Reel.

    Instagram first prepares the video. We wait until it says FINISHED.
    Only then do we ask Instagram to publish it.
    """
    if not settings.publish_enabled:
        raise InstagramPublishError("Publishing is OFF in the settings.")

    if not settings.instagram_is_ready:
        raise InstagramPublishError(
            "Add INSTAGRAM_USER_ID and META_ACCESS_TOKEN to the .env file."
        )

    account_address = (
        f"https://graph.facebook.com/"
        f"{settings.meta_graph_version}/{settings.instagram_user_id}"
    )
    headers = {"Authorization": f"Bearer {settings.meta_access_token}"}

    try:
        # Step 1: Ask Instagram to prepare a Reel from our public video link.
        create_reply = httpx.post(
            f"{account_address}/media",
            data={
                "media_type": "REELS",
                "video_url": video_link,
                "caption": caption,
            },
            headers=headers,
            timeout=60,
        )
        create_reply.raise_for_status()

        container_id = create_reply.json().get("id")
        if not container_id:
            raise InstagramPublishError("Instagram did not give us a video container ID.")

        # Step 2: Check whether Instagram has finished preparing the video.
        video_status = None

        for _attempt in range(30):
            status_reply = httpx.get(
                f"https://graph.facebook.com/{settings.meta_graph_version}/{container_id}",
                params={
                    "fields": "status_code",
                    "access_token": settings.meta_access_token,
                },
                timeout=30,
            )
            status_reply.raise_for_status()
            video_status = status_reply.json().get("status_code")

            if video_status == "FINISHED":
                break

            if video_status in {"ERROR", "EXPIRED"}:
                raise InstagramPublishError(
                    f"Instagram could not prepare the video. Status: {video_status}"
                )

            time.sleep(2)

        if video_status != "FINISHED":
            raise InstagramPublishError("Instagram took too long to prepare the video.")

        # Step 3: Tell Instagram to publish the prepared Reel.
        publish_reply = httpx.post(
            f"{account_address}/media_publish",
            data={"creation_id": container_id},
            headers=headers,
            timeout=60,
        )
        publish_reply.raise_for_status()

        instagram_media_id = publish_reply.json().get("id")
        if not instagram_media_id:
            raise InstagramPublishError("Instagram did not confirm the published Reel.")

        return instagram_media_id

    except httpx.HTTPError as error:
        raise InstagramPublishError(f"Instagram API request failed: {error}") from error
