from platform_common import BaseServiceSettings


class IdentitySettings(BaseServiceSettings):
    service_name: str = "identity-service"
    mysql_dsn: str = "mysql+pymysql://jobseeking:jobseeking@mysql:3306/identity"
    jwt_secret: str = "change-me"
    stripe_secret_key: str = ""
