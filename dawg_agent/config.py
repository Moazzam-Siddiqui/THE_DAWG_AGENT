"""Read settings from the .env file.

A setting is just an instruction the robot reads when it starts.
Keep passwords and access tokens in .env, never in Python files.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings used by the robot, with safe defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Where the robot saves its work.
    database_url: str = "sqlite:///./data/dawg_agent.db"
    output_dir: Path = Path("assets/rendered")
    timezone: str = "Asia/Kolkata"

    # Safety: the robot must not publish unless we switch this on.
    publish_enabled: bool = False
    require_approval: bool = True
    max_posts_per_day: int = Field(default=3, ge=1, le=25)
    min_post_interval_minutes: int = Field(default=180, ge=15)
    publish_window_start: str = "07:00"
    publish_window_end: str = "22:00"
    scheduler_poll_seconds: int = Field(default=30, ge=5)
    max_retries: int = Field(default=3, ge=0, le=10)

    # How to make the video.
    ffmpeg_binary: str = "ffmpeg"
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    max_duration_seconds: int = Field(default=12, ge=6, le=12)
    audio_required: bool = False
    audio_source_path: Path | None = None

    # Cloudinary: stores a video and gives us a public link.
    cloudinary_cloud_name: str = "tlrvr5kk"
    cloudinary_upload_preset: str = "dog_reels_upload"
    cloudinary_folder: str = "dog-reels"

    # Instagram: these are secret account credentials.
    meta_graph_version: str = "v23.0"
    instagram_user_id: str | None = None
    meta_access_token: str | None = None
    api_key: str | None = None

    @property
    def instagram_is_ready(self) -> bool:
        """True only when both Instagram details have been supplied."""
        return bool(self.instagram_user_id and self.meta_access_token)


@lru_cache
def get_settings() -> Settings:
    """Load settings once and reuse them."""
    return Settings()
