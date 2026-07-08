from platform_common import BaseServiceSettings


class CommunicationSettings(BaseServiceSettings):
    service_name: str = "communication-service"
    mysql_dsn: str = "mysql+pymysql://jobseeking:jobseeking@mysql:3306/communication"
    redis_url: str = "redis://redis:6379/0"
