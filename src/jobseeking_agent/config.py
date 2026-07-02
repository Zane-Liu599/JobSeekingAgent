from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "sqlite:///data/jobseeking_agent.db"

    browser_headless: bool = False
    browser_slow_mo_ms: int = Field(default=100, ge=0)
    user_agent: str = "JobSeekingAgent/0.1"

    request_timeout_seconds: int = Field(default=30, gt=0)
    crawl_delay_seconds: int = Field(default=3, ge=0)
    max_jobs_per_source: int = Field(default=50, gt=0)

    candidate_name: str = ""
    candidate_email: str = ""
    candidate_phone: str = ""
    candidate_location: str = ""
    resume_path: str = "./resumes/default.pdf"
    cover_letter_template_path: str = "./cover_letters/default.md"

    target_titles: str = "Software Engineer,Backend Engineer,Data Engineer"
    target_locations: str = "Remote,Sydney,Melbourne"
    min_salary: str = ""
    work_authorization: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"


def get_settings() -> Settings:
    return Settings()
