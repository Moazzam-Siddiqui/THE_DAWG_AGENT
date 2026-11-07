import subprocess
from pathlib import Path
from PIL import Image
from dawg_agent.config import Settings

class RenderError(RuntimeError):
    pass

def _run(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
    except FileNotFoundError as exc:
        raise RenderError("FFmpeg was not found. Install FFmpeg and ensure it is on PATH.") from exc
    if result.returncode != 0:
        raise RenderError(f"FFmpeg failed: {result.stderr[-1800:]}")
    return result.stderr

def render_reel(image_path: str | Path, output_path: str | Path, duration: int,
                settings: Settings, audio_path: str | Path | None = None) -> Path:
    image_path, output_path = Path(image_path), Path(output_path)
    if not image_path.is_file():
        raise RenderError(f"Image does not exist: {image_path}")
    if duration < 6 or duration > settings.max_duration_seconds:
        raise RenderError("Duration must be 6 seconds or longer and within configured maximum.")
    try:
        with Image.open(image_path) as image:
            image.verify()
    except Exception as exc:
        raise RenderError(f"Invalid image: {exc}") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    vf = (f"scale={settings.video_width}:{settings.video_height}:force_original_aspect_ratio=increase,"
          f"crop={settings.video_width}:{settings.video_height},"
          f"zoompan=z='min(zoom+0.0008,1.04)':d={duration * settings.video_fps}:"
          f"s={settings.video_width}x{settings.video_height}:fps={settings.video_fps},"
          "setsar=1,format=yuv420p")
    cmd = [settings.ffmpeg_binary, "-y", "-loop", "1", "-i", str(image_path)]
    audio = Path(audio_path) if audio_path else None
    has_audio = bool(audio and audio.is_file())
    if has_audio:
        cmd += ["-stream_loop", "-1", "-i", str(audio)]
    elif settings.audio_required:
        raise RenderError("Audio is required but no valid audio file was supplied.")
    cmd += ["-t", str(duration), "-vf", vf, "-r", str(settings.video_fps),
            "-c:v", "libx264", "-preset", "medium", "-crf", "22", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart"]
    if has_audio:
        cmd += ["-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "128k"]
    else:
        cmd += ["-an"]
    cmd.append(str(output_path))
    _run(cmd)
    validate_video(output_path, settings, require_audio=bool(has_audio))
    return output_path

def validate_video(path: str | Path, settings: Settings, require_audio: bool = False) -> dict:
    path = Path(path)
    if not path.is_file() or path.stat().st_size < 1024:
        raise RenderError("Rendered video is missing or unexpectedly small.")
    probe = _run([settings.ffmpeg_binary, "-i", str(path), "-f", "null", "-"])
    dimensions = f"{settings.video_width}x{settings.video_height}"
    if dimensions not in probe:
        raise RenderError("Output video dimensions do not match configured vertical dimensions.")
    audio_present = "Audio:" in probe
    if require_audio and not audio_present:
        raise RenderError("Expected audio stream is missing.")
    return {"path": str(path), "bytes": path.stat().st_size,
            "dimensions": dimensions, "audio_present": audio_present}
