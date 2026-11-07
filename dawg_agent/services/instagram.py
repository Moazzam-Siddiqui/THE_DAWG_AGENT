import time
import httpx

from dawg_agent.config import Settings


class InstagramPublishError(RuntimeError):
    pass


def publish_reel(media_url: str, caption: str, settings: Settings) -> str:
    if not settings.publish_enabled:
        raise InstagramPublishError("Publishing is disabled. Set PUBLISH_ENABLED=true only after review.")
    if not settings.instagram_configured:
        raise InstagramPublishError("INSTAGRAM_USER_ID and META_ACCESS_TOKEN are required.")
    base = f"https://graph.facebook.com/{settings.meta_graph_version}/{settings.instagram_user_id}"
    headers = {"Authorization": f"Bearer {settings.meta_access_token}"}
    try:
        response = httpx.post(
            f"{base}/media",
            data={"media_type": "REELS", "video_url": media_url, "caption": caption},
            headers=headers, timeout=60)
        response.raise_for_status()
        creation_id = response.json().get("id")
        if not creation_id:
            raise InstagramPublishError("Instagram did not return a container ID.")

        # Poll container status before publishing; do not publish an unfinished upload.
        status_code = None
        for _ in range(30):
            status_response = httpx.get(
                f"https://graph.facebook.com/{settings.meta_graph_version}/{creation_id}",
                params={"fields": "status_code", "access_token": settings.meta_access_token},
                timeout=30)
            status_response.raise_for_status()
            status_code = status_response.json().get("status_code")
            if status_code == "FINISHED":
                break
            if status_code in {"ERROR", "EXPIRED"}:
                raise InstagramPublishError(f"Instagram media container status: {status_code}")
            time.sleep(2)
        if status_code != "FINISHED":
            raise InstagramPublishError(f"Instagram container did not finish; last status: {status_code}")

        publish_response = httpx.post(
            f"{base}/media_publish",
            data={"creation_id": creation_id}, headers=headers, timeout=60)
        publish_response.raise_for_status()
        media_id = publish_response.json().get("id")
        if not media_id:
            raise InstagramPublishError("Instagram publish response did not include media ID.")
        return media_id
    except httpx.HTTPError as exc:
        raise InstagramPublishError(f"Instagram Graph API error: {exc}") from exc
