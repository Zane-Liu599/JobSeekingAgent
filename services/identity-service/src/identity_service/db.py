from __future__ import annotations

import pymysql

from identity_service.config import settings


def mysql_connection():
    return pymysql.connect(
        host=mysql_host(),
        port=mysql_port(),
        user=mysql_user(),
        password=mysql_password(),
        database=mysql_database(),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def mysql_host() -> str:
    return dsn_part_after("@").split(":", 1)[0]


def mysql_port() -> int:
    host_part = dsn_part_after("@").split("/", 1)[0]
    if ":" not in host_part:
        return 3306
    return int(host_part.rsplit(":", 1)[1])


def mysql_user() -> str:
    return settings.mysql_dsn.split("://", 1)[1].split(":", 1)[0]


def mysql_password() -> str:
    return settings.mysql_dsn.split("://", 1)[1].split("@", 1)[0].split(":", 1)[1]


def mysql_database() -> str:
    return settings.mysql_dsn.rsplit("/", 1)[1]


def dsn_part_after(marker: str) -> str:
    return settings.mysql_dsn.split(marker, 1)[1]


def init_identity_db() -> None:
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(120) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                phone VARCHAR(40) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                created_at DATETIME NOT NULL,
                verified_at DATETIME NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                token_hash VARCHAR(128) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                used_at DATETIME NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                token_hash VARCHAR(128) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
