import json
import subprocess
from pathlib import Path

from PIL import Image

from dawg_agent.config import Settings


class RenderError(RuntimeError):
    pass


def _run(command: list[str]) -> None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RenderError("FFmpeg was not found. Install FFmpeg and ensure it is on PATH.") from exc
    if result.returncode != 0:
        raise RenderError(f"FFmpeg failed: {result.stderr[-2000:]}")


def render_reel(image_path: str | Path, output_path: str | Path, duration: int, settings: Settings,
                audio_path: str | Path | None = None) -> Path:
    image_path, output_path = Path(image_path), Path(output_path)
    if not image_path.is_file():
        raise RenderError(f"Image does not exist: {image_path}")
    if duration < 6 or duration > settings.max_duration_seconds:
        raise RenderError("Duration must be between 6 and configured maximum seconds.")

    try:
        with Image.open(image_path) as image:
            image.verify()
    except Exception as exc:
        raise RenderError(f"Invalid image: {exc}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Scale to fill canvas, then crop to 9:16. A gentle zoom creates motion from a still.
    video_filter = (
        f"scale={settings.video_width}:{settings.video_height}:force_original_aspect_ratio=increase,"
        f"crop={settings.video_width}:{settings.video_height},"
        f"zoompan=z='min(zoom+0.0008,1.04)':d={duration * settings.video_fps}:"
        f"s={settings.video_width}x{settings.video_height}:fps={settings.video_fps},"
        "setsar=1,format=yuv420p"
    )
    command = [
        settings.ffmpeg_binary, "-y", "-loop", "1", "-i", str(image_path),
    ]
    valid_audio = Path(audio_path) if audio_path else None
    if valid_audio and valid_audio.is_file():
        command += ["-stream_loop", "-1", "-i", str(valid_audio)]
    command += ["-t", str(duration), "-vf", video_filter, "-r", str(settings.video_fps),
                "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-movflags", "+faststart"]
    if valid_audio and valid_audio.is_file():
        command += ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "128k",
                    "-shortest"]
    else:
        if settings.audio_required:
            raise RenderError("Audio is required but no valid audio file was supplied.")
        command += ["-an"]
    command.append(str(output_path))
    _run(command)
    validate_video(output_path, settings, duration, require_audio=bool(valid_audio))
    return output_path


def validate_video(path: str | Path, settings: Settings, expected_duration: int | None = None,
                   require_audio: bool = False) -> dict:
    path = Path(path)
    if not path.is_file() or path.stat().st_size < 1024:
        raise RenderError("Rendered video is missing or unexpectedly small.")
    command = [settings.ffmpeg_binary, "-i", str(path), "-f", "null", "-"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RenderError("FFmpeg was not found.") from exc
    probe = result.stderr
    if f"{settings.video_width}x{settings.video_height}" not in probe:
        raise RenderError("Output video does not have the configured vertical dimensions.")
    if require_audio and "Audio:" not in probe:
        raise RenderError("Expected audio stream was not found in output.")
    return {"path": str(path), "bytes": path.stat().st_size,
            "dimensions": f"{settings.video_width}x{settings.video_height}",
            "expected_duration_seconds": expected_duration, "audio_present": "Audio:" in probe}
