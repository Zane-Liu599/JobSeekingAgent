from platform_common import BaseServiceSettings
from pydantic import Field


class CrawlerSettings(BaseServiceSettings):
    service_name: str = "crawler-service"
    database_url: str = "sqlite:////app/data/jobseeking_agent.db"
    default_keywords: str = Field(
        default="software engineer,backend engineer,full stack developer",
        validation_alias="CRAWLER_DEFAULT_KEYWORDS",
    )
    default_locations: str = Field(
        default="Sydney,Melbourne,Remote",
        validation_alias="CRAWLER_DEFAULT_LOCATIONS",
    )
    default_platforms: str = Field(
        default="seek,linkedin,indeed",
        validation_alias="CRAWLER_DEFAULT_PLATFORMS",
    )
    admin_token: str = Field(default="", validation_alias="CRAWLER_ADMIN_TOKEN")
    provider: str = Field(default="auto", validation_alias="CRAWLER_PROVIDER")
    official_apply_only: bool = Field(
        default=True,
        validation_alias="CRAWLER_OFFICIAL_APPLY_ONLY",
    )
    allow_search_discovery: bool = Field(
        default=True,
        validation_alias="CRAWLER_ALLOW_SEARCH_DISCOVERY",
    )
    jobspy_results_wanted: int = Field(
        default=25,
        validation_alias="JOBSPY_RESULTS_WANTED",
    )
    jobspy_hours_old: int | None = Field(
        default=168,
        validation_alias="JOBSPY_HOURS_OLD",
    )
    jobspy_country_indeed: str = Field(
        default="Australia",
        validation_alias="JOBSPY_COUNTRY_INDEED",
    )
    jobspy_linkedin_fetch_description: bool = Field(
        default=True,
        validation_alias="JOBSPY_LINKEDIN_FETCH_DESCRIPTION",
    )
    jobspy_proxies: str = Field(default="", validation_alias="JOBSPY_PROXIES")
    user_agent: str = Field(default="", validation_alias="USER_AGENT")


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]
