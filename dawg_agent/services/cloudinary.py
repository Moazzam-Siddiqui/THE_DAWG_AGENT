import httpx
from pathlib import Path

from dawg_agent.config import Settings


class UploadError(RuntimeError):
    pass


def upload_video(path: str | Path, settings: Settings) -> str:
    if not settings.cloudinary_configured:
        raise UploadError("Cloudinary cloud name and unsigned upload preset must be configured.")
    file_path = Path(path)
    if not file_path.is_file():
        raise UploadError(f"Video does not exist: {file_path}")
    url = f"https://api.cloudinary.com/v1_1/{settings.cloudinary_cloud_name}/video/upload"
    data = {"upload_preset": settings.cloudinary_upload_preset, "folder": settings.cloudinary_folder}
    try:
        with file_path.open("rb") as media:
            response = httpx.post(url, data=data, files={"file": (file_path.name, media, "video/mp4")},
                                  timeout=180)
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise UploadError(f"Cloudinary upload failed: {exc}") from exc
    secure_url = payload.get("secure_url")
    if not secure_url:
        raise UploadError("Cloudinary response did not include secure_url.")
    return secure_url
