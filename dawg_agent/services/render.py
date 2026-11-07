"""Make a vertical video from one picture.

FFmpeg is the video-making tool. Pillow checks that the picture can be opened.
"""
import subprocess
from pathlib import Path

from PIL import Image

from dawg_agent.config import Settings


class RenderError(RuntimeError):
    """The video could not be made or did not pass its checks."""


def run_ffmpeg(command: list[str]) -> str:
    """Run FFmpeg and return what it printed."""
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as error:
        raise RenderError(
            "FFmpeg is missing. Install it, then make sure the 'ffmpeg' command works."
        ) from error

    if result.returncode != 0:
        raise RenderError(f"FFmpeg could not finish the video:\n{result.stderr[-1800:]}")

    return result.stderr


def check_video(video_path: Path, settings: Settings, audio_must_exist: bool = False) -> dict:
    """Check that the video file exists and has the right picture size."""
    if not video_path.is_file():
        raise RenderError("The video file was not created.")
    if video_path.stat().st_size < 1024:
        raise RenderError("The video file is too small. Something probably went wrong.")

    video_info = run_ffmpeg([
        settings.ffmpeg_binary,
        "-i", str(video_path),
        "-f", "null",
        "-",
    ])

    correct_size = f"{settings.video_width}x{settings.video_height}"
    if correct_size not in video_info:
        raise RenderError(f"The video is not {correct_size} pixels.")

    has_sound = "Audio:" in video_info
    if audio_must_exist and not has_sound:
        raise RenderError("Sound was expected, but the video has no sound.")

    return {
        "file": str(video_path),
        "size_in_bytes": video_path.stat().st_size,
        "picture_size": correct_size,
        "has_sound": has_sound,
    }


def render_reel(
    image_path: str | Path,
    output_path: str | Path,
    duration: int,
    settings: Settings,
    audio_path: str | Path | None = None,
) -> Path:
    """Turn a still picture into a short vertical MP4."""
    picture = Path(image_path)
    video = Path(output_path)

    if not picture.is_file():
        raise RenderError(f"I cannot find this picture: {picture}")

    if not 6 <= duration <= settings.max_duration_seconds:
        raise RenderError("A Reel must be 6 seconds or longer and within the configured limit.")

    try:
        with Image.open(picture) as opened_picture:
            opened_picture.verify()
    except Exception as error:
        raise RenderError(f"I cannot open this picture: {error}") from error

    video.parent.mkdir(parents=True, exist_ok=True)

    # First fill the tall video frame. Then cut away the extra edges.
    # zoompan adds a tiny movement so the picture does not look completely frozen.
    video_filter = (
        f"scale={settings.video_width}:{settings.video_height}:"
        "force_original_aspect_ratio=increase,"
        f"crop={settings.video_width}:{settings.video_height},"
        f"zoompan=z='min(zoom+0.0008,1.04)':d={duration * settings.video_fps}:"
        f"s={settings.video_width}x{settings.video_height}:fps={settings.video_fps},"
        "setsar=1,format=yuv420p"
    )

    command = [
        settings.ffmpeg_binary,
        "-y",
        "-loop", "1",
        "-i", str(picture),
    ]

    sound_file = Path(audio_path) if audio_path else None
    sound_is_ready = bool(sound_file and sound_file.is_file())

    if sound_is_ready:
        command.extend(["-stream_loop", "-1", "-i", str(sound_file)])
    elif settings.audio_required:
        raise RenderError("This project needs an audio file, but none was supplied.")

    command.extend([
        "-t", str(duration),
        "-vf", video_filter,
        "-r", str(settings.video_fps),
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
    ])

    if sound_is_ready:
        command.extend(["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "128k"])
    else:
        command.append("-an")

    command.append(str(video))
    run_ffmpeg(command)
    check_video(video, settings, audio_must_exist=sound_is_ready)
    return video
