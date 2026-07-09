from __future__ import annotations

from datetime import datetime

from identity_service.config import EMAIL_VERIFICATION_TTL, SESSION_TTL
from identity_service.db import mysql_connection
from identity_service.security import hash_token
from identity_service.time_utils import utc_now


def create_user_with_verification_token(
    *,
    name: str,
    email: str,
    phone: str,
    password_hash: str,
    token: str,
) -> int:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (name, email, phone, password_hash, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, phone, password_hash, now),
        )
        user_id = cursor.lastrowid
        create_verification_token(cursor, user_id, token, now)
        return user_id


def create_verification_token(cursor, user_id: int, token: str, created_at: datetime) -> int:
    cursor.execute(
        """
        INSERT INTO email_verification_tokens
            (user_id, token_hash, expires_at, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, hash_token(token), created_at + EMAIL_VERIFICATION_TTL, created_at),
    )
    return cursor.lastrowid


def get_user_by_email(email: str) -> dict | None:
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        return cursor.fetchone()


def get_user_from_session(token: str) -> dict | None:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT users.*
            FROM user_sessions
            JOIN users ON users.id = user_sessions.user_id
            WHERE user_sessions.token_hash = %s
              AND user_sessions.expires_at > %s
            """,
            (hash_token(token), now),
        )
        return cursor.fetchone()


def create_session(user_id: int, token: str) -> None:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_sessions (user_id, token_hash, expires_at, created_at)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, hash_token(token), now + SESSION_TTL, now),
        )


def get_verification_record(token: str) -> dict | None:
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT evt.*, users.email_verified
            FROM email_verification_tokens evt
            JOIN users ON users.id = evt.user_id
            WHERE evt.token_hash = %s
            """,
            (hash_token(token),),
        )
        return cursor.fetchone()


def verify_user_email(user_id: int, token_id: int) -> None:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            "UPDATE users SET email_verified = TRUE, verified_at = %s WHERE id = %s",
            (now, user_id),
        )
        cursor.execute(
            "UPDATE email_verification_tokens SET used_at = %s WHERE id = %s",
            (now, token_id),
        )


def resend_verification_token(user_id: int, token: str) -> int:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE email_verification_tokens
            SET used_at = %s
            WHERE user_id = %s AND used_at IS NULL
            """,
            (now, user_id),
        )
        return create_verification_token(cursor, user_id, token, now)


def latest_pending_token_created_at(user_id: int) -> datetime | None:
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT created_at
            FROM email_verification_tokens
            WHERE user_id = %s AND used_at IS NULL
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (user_id,),
        )
        latest_token = cursor.fetchone()
        return latest_token["created_at"] if latest_token else None


def mark_verification_token_used(token_id: int) -> None:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            "UPDATE email_verification_tokens SET used_at = %s WHERE id = %s",
            (now, token_id),
        )


def delete_user(user_id: int) -> None:
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))


def cleanup_expired_unverified_user(email: str) -> None:
    now = utc_now().replace(tzinfo=None)
    with mysql_connection() as connection, connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT users.id, MAX(email_verification_tokens.expires_at) AS expires_at
            FROM users
            LEFT JOIN email_verification_tokens
                ON email_verification_tokens.user_id = users.id
            WHERE users.email = %s AND users.email_verified = FALSE
            GROUP BY users.id
            """,
            (email,),
        )
        record = cursor.fetchone()
        if record and record["expires_at"] and record["expires_at"] < now:
            cursor.execute("DELETE FROM users WHERE id = %s", (record["id"],))
