from platform_common import BaseServiceSettings


class AISettings(BaseServiceSettings):
    service_name: str = "ai-service"
    postgres_dsn: str = "postgresql+psycopg://jobseeking:jobseeking@postgres:5432/ai"
    redis_url: str = "redis://redis:6379/1"
    minio_endpoint: str = "http://minio:9000"
    crawler_internal_url: str = "http://crawler-service:8000"
    crawler_admin_token: str = ""
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
