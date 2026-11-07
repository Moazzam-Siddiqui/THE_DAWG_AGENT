import time
import httpx
from dawg_agent.config import Settings

class InstagramPublishError(RuntimeError):
    pass

def publish_reel(media_url: str, caption: str, settings: Settings) -> str:
    if not settings.publish_enabled:
        raise InstagramPublishError("Publishing is disabled by safety configuration.")
    if not settings.instagram_configured:
        raise InstagramPublishError("Instagram user ID and Meta access token are required.")
    base = f"https://graph.facebook.com/{settings.meta_graph_version}/{settings.instagram_user_id}"
    headers = {"Authorization": f"Bearer {settings.meta_access_token}"}
    try:
        response = httpx.post(f"{base}/media",
            data={"media_type": "REELS", "video_url": media_url, "caption": caption},
            headers=headers, timeout=60)
        response.raise_for_status()
        container_id = response.json().get("id")
        if not container_id:
            raise InstagramPublishError("Instagram did not return a media container ID.")
        status_code = None
        for _ in range(30):
            check = httpx.get(f"https://graph.facebook.com/{settings.meta_graph_version}/{container_id}",
                params={"fields": "status_code", "access_token": settings.meta_access_token},
                timeout=30)
            check.raise_for_status()
            status_code = check.json().get("status_code")
            if status_code == "FINISHED":
                break
            if status_code in {"ERROR", "EXPIRED"}:
                raise InstagramPublishError(f"Instagram container status: {status_code}")
            time.sleep(2)
        if status_code != "FINISHED":
            raise InstagramPublishError(f"Instagram container did not finish: {status_code}")
        published = httpx.post(f"{base}/media_publish",
            data={"creation_id": container_id}, headers=headers, timeout=60)
        published.raise_for_status()
        media_id = published.json().get("id")
        if not media_id:
            raise InstagramPublishError("Instagram response did not include published media ID.")
        return media_id
    except httpx.HTTPError as exc:
        raise InstagramPublishError(f"Instagram Graph API request failed: {exc}") from exc
