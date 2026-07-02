from jobseeking_agent.config import get_settings


def browser_launch_options() -> dict[str, int | bool]:
    settings = get_settings()
    return {
        "headless": settings.browser_headless,
        "slow_mo": settings.browser_slow_mo_ms,
    }
