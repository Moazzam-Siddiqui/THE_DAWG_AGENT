"""Regression tests for input validation in the video renderer."""
import pytest
from PIL import Image

from dawg_agent.config import Settings
from dawg_agent.services.render import RenderError, render_reel


def test_missing_selected_audio_fails_instead_of_silently_rendering_silent_video(tmp_path):
    image_path = tmp_path / "dog.png"
    Image.new("RGB", (64, 64), "white").save(image_path)

    with pytest.raises(RenderError, match="selected audio file does not exist"):
        render_reel(
            image_path=image_path,
            output_path=tmp_path / "output.mp4",
            duration=9,
            settings=Settings(),
            audio_path=tmp_path / "missing.mp3",
        )


def test_audio_can_be_optional_for_a_silent_preview(tmp_path, monkeypatch):
    image_path = tmp_path / "dog.png"
    Image.new("RGB", (64, 64), "white").save(image_path)

    calls = []

    def fake_ffmpeg(command):
        calls.append(command)
        (tmp_path / "output.mp4").write_bytes(b"fake video")
        return ""

    monkeypatch.setattr("dawg_agent.services.render.run_ffmpeg", fake_ffmpeg)
    monkeypatch.setattr(
        "dawg_agent.services.render.check_video",
        lambda *args, **kwargs: {"has_sound": False},
    )

    result = render_reel(
        image_path=image_path,
        output_path=tmp_path / "output.mp4",
        duration=9,
        settings=Settings(),
        audio_path=None,
    )

    assert result == tmp_path / "output.mp4"
    assert calls
    assert "-an" in calls[0]
