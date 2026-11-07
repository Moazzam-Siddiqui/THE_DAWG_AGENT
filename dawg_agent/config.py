from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    database_url: str = "sqlite:///./data/dawg_agent.db"
    timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"
    output_dir: Path = Path("assets/rendered")

    publish_enabled: bool = False
    require_approval: bool = True
    max_posts_per_day: int = Field(default=3, ge=1, le=25)
    min_post_interval_minutes: int = Field(default=180, ge=15, le=1440)
    publish_window_start: str = "07:00"
    publish_window_end: str = "22:00"
    scheduler_poll_seconds: int = Field(default=30, ge=5, le=3600)
    max_retries: int = Field(default=3, ge=0, le=10)

    ffmpeg_binary: str = "ffmpeg"
    video_width: int = 1080
    video_height: int = 1920
    video_fps: int = 30
    default_duration_seconds: int = Field(default=9, ge=6, le=12)
    max_duration_seconds: int = Field(default=12, ge=6, le=12)
    use_audio_by_default: bool = True
    audio_required: bool = False
    audio_source_path: Path | None = None

    cloudinary_cloud_name: str = "tlrvr5kk"
    cloudinary_upload_preset: str = "dog_reels_upload"
    cloudinary_folder: str = "dog-reels"

    meta_graph_version: str = "v23.0"
    instagram_user_id: str | None = None
    meta_access_token: str | None = None
    api_key: str | None = None

    @field_validator("publish_window_start", "publish_window_end")
    @classmethod
    def validate_clock_time(cls, value: str) -> str:
        try:
            hour, minute = (int(part) for part in value.split(":"))
        except (ValueError, TypeError) as exc:
            raise ValueError("Clock time must be HH:MM") from exc
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Clock time must be HH:MM")
        return value

    @property
    def cloudinary_configured(self) -> bool:
        return bool(self.cloudinary_cloud_name and self.cloudinary_upload_preset)

    @property
    def instagram_configured(self) -> bool:
        return bool(self.instagram_user_id and self.meta_access_token)


@lru_cache
def get_settings() -> Settings:
    return Settings()
