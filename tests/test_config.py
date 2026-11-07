"""Check that the robot starts with safe settings."""
from dawg_agent.config import Settings


def test_publishing_is_off_when_the_robot_is_new():
    settings = Settings()

    assert settings.publish_enabled is False


def test_robot_starts_with_a_small_daily_post_limit():
    settings = Settings()

    assert settings.max_posts_per_day == 3
    assert settings.min_post_interval_minutes == 180
