from pathlib import Path
import httpx
from dawg_agent.config import Settings

class UploadError(RuntimeError):
    pass

def upload_video(path: str | Path, settings: Settings) -> str:
    media_path = Path(path)
    if not settings.cloudinary_configured:
        raise UploadError("Cloudinary configuration is incomplete.")
    if not media_path.is_file():
        raise UploadError(f"Video does not exist: {media_path}")
    endpoint = f"https://api.cloudinary.com/v1_1/{settings.cloudinary_cloud_name}/video/upload"
    try:
        with media_path.open("rb") as stream:
            response = httpx.post(endpoint,
                data={"upload_preset": settings.cloudinary_upload_preset,
                      "folder": settings.cloudinary_folder},
                files={"file": (media_path.name, stream, "video/mp4")}, timeout=180)
        response.raise_for_status()
        result = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise UploadError(f"Cloudinary upload failed: {exc}") from exc
    url = result.get("secure_url")
    if not url:
        raise UploadError("Cloudinary response did not contain secure_url.")
    return url
