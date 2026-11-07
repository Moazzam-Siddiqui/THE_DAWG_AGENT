from dawg_agent.config import Settings

def test_publish_disabled_by_default():
    assert Settings().publish_enabled is False

def test_default_rate_controls_are_conservative():
    cfg = Settings()
    assert cfg.max_posts_per_day == 3
    assert cfg.min_post_interval_minutes >= 15
