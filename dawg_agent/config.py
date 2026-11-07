"""Read settings from the local .env file."""
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings used by the local-first agent."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./data/dawg_agent.db"
    output_dir: Path = Path("assets/rendered")
    timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"

    # Publishing remains disabled until the Instagram app and account are configured.
    publish_enabled: bool = False
    require_approval: bool = False
    max_posts_per_day: int = Field(default=3, ge=1, le=25)
    min_post_interval_minutes: int = Field(default=180, ge=15)
    publish_window_start: str = "07:00"
    publish_window_end: str = "22:00"
    scheduler_poll_seconds: int = Field(default=30, ge=5)
    max_retries: int = Field(default=3, ge=0, le=10)

    ffmpeg_binary: str = "ffmpeg"
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    max_duration_seconds: int = Field(default=12, ge=6, le=12)
    default_duration_seconds: int = Field(default=9, ge=6, le=12)
    audio_required: bool = True
    audio_source_path: Path | None = None

    # Point these folders inside the Google Drive for desktop synced directory.
    drive_inbox_dir: Path = Path("drive/01_INCOMING_IMAGES")
    drive_processed_dir: Path = Path("drive/04_PROCESSED_IMAGES")
    drive_failed_dir: Path = Path("drive/05_FAILED_IMAGES")
    default_caption: str = "What da dog doin? 🐶"
    default_hashtags: list[str] = ["dogs", "dogreels", "WhatDaDogDoing"]

    meta_graph_version: str = "v23.0"
    instagram_user_id: str | None = None
    meta_access_token: str | None = None
    instagram_processing_attempts: int = Field(default=60, ge=1, le=180)
    instagram_processing_poll_seconds: int = Field(default=5, ge=1, le=30)
    api_key: str | None = None

    @property
    def instagram_is_ready(self) -> bool:
        return bool(self.instagram_user_id and self.meta_access_token)


@lru_cache
def get_settings() -> Settings:
    return Settings()
