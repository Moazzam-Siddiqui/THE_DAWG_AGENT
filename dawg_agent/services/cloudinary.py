"""Send finished videos to Cloudinary.

Cloudinary stores the video online and returns a web address. Instagram can
then read the video from that address.
"""
from pathlib import Path

import httpx

from dawg_agent.config import Settings


class UploadError(RuntimeError):
    """The video could not be sent to Cloudinary."""


def upload_video(video_path: str | Path, settings: Settings) -> str:
    """Upload one MP4 and return its public HTTPS address."""
    video_file = Path(video_path)

    if not settings.cloudinary_cloud_name or not settings.cloudinary_upload_preset:
        raise UploadError("Add the Cloudinary cloud name and upload preset to your .env file.")

    if not video_file.is_file():
        raise UploadError(f"I cannot find the video file: {video_file}")

    upload_address = (
        f"https://api.cloudinary.com/v1_1/"
        f"{settings.cloudinary_cloud_name}/video/upload"
    )

    upload_options = {
        "upload_preset": settings.cloudinary_upload_preset,
        "folder": settings.cloudinary_folder,
    }

    try:
        with video_file.open("rb") as video:
            response = httpx.post(
                upload_address,
                data=upload_options,
                files={"file": (video_file.name, video, "video/mp4")},
                timeout=180,
            )

        response.raise_for_status()
        cloudinary_reply = response.json()

    except (httpx.HTTPError, ValueError) as error:
        raise UploadError(f"Cloudinary could not upload the video: {error}") from error

    public_video_link = cloudinary_reply.get("secure_url")
    if not public_video_link:
        raise UploadError("Cloudinary did not give us a public video link.")

    return public_video_link
