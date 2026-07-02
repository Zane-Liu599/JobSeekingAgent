from jobseeking_agent.config import Settings


def test_settings_defaults_are_cross_platform_safe() -> None:
    settings = Settings()

    assert settings.app_env == "development"
    assert settings.request_timeout_seconds > 0
    assert settings.max_jobs_per_source > 0
    assert settings.resume_path.endswith(".pdf")
