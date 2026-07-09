from platform_common import BaseServiceSettings
from pydantic import Field


class IdentitySettings(BaseServiceSettings):
    service_name: str = "identity-service"
    mysql_dsn: str = Field(
        default="mysql+pymysql://jobseeking:jobseeking@mysql:3306/identity",
        validation_alias="MYSQL_DSN",
    )
    jwt_secret: str = Field(default="change-me", validation_alias="JWT_SECRET")
    stripe_secret_key: str = ""
    app_public_url: str = Field(default="http://localhost:8080", validation_alias="APP_PUBLIC_URL")
    smtp_host: str = Field(default="", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")
    smtp_username: str = Field(default="", validation_alias="SMTP_USERNAME")
    smtp_password: str = Field(default="", validation_alias="SMTP_PASSWORD")
    smtp_from_email: str = Field(
        default="noreply@jobseeking-agent.local",
        validation_alias="SMTP_FROM_EMAIL",
    )
