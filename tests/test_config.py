"""Check safe defaults for the local-first agent."""
from dawg_agent.config import Settings


def test_publishing_is_off_until_instagram_is_configured():
    settings = Settings()
    assert settings.publish_enabled is False


def test_automatic_mode_does_not_require_manual_approval():
    assert Settings().require_approval is False


def test_campaign_audio_is_required_by_default():
    assert Settings().audio_required is True


def test_daily_limits_remain_conservative():
    settings = Settings()
    assert settings.max_posts_per_day == 3
    assert settings.min_post_interval_minutes == 180
