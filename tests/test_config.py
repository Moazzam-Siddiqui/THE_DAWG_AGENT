"""Check that the robot starts with safe settings."""
from dawg_agent.config import Settings


def test_publishing_is_off_when_the_robot_is_new():
    settings = Settings()

    assert settings.publish_enabled is False


def test_robot_starts_with_a_small_daily_post_limit():
    settings = Settings()

    assert settings.max_posts_per_day == 3
    assert settings.min_post_interval_minutes == 180



def test_worker_log_level_has_a_safe_default():
    settings = Settings()

    assert settings.log_level == "INFO"


def test_publishing_limits_are_conservative_by_default():
    settings = Settings()

    assert settings.publish_enabled is False
    assert settings.require_approval is True
    assert settings.max_posts_per_day == 3
    assert settings.min_post_interval_minutes == 180
