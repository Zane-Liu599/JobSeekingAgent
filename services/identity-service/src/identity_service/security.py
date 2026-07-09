from __future__ import annotations

import base64
import hashlib
import hmac
import secrets

from identity_service.config import settings


def password_policy_errors(password: str) -> list[str]:
    errors: list[str] = []
    if len(password) < 10:
        errors.append("Use at least 10 characters.")
    if not any(char.islower() for char in password):
        errors.append("Add a lowercase letter.")
    if not any(char.isupper() for char in password):
        errors.append("Add an uppercase letter.")
    if not any(char.isdigit() for char in password):
        errors.append("Add a number.")
    if not any(not char.isalnum() for char in password):
        errors.append("Add a symbol.")
    common = {"password", "password123", "qwerty123", "letmein123", "admin123"}
    if password.lower() in common:
        errors.append("Avoid common passwords.")
    return errors


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    salt_text = base64.b64encode(salt).decode()
    digest_text = base64.b64encode(digest).decode()
    return f"pbkdf2_sha256$210000${salt_text}${digest_text}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, rounds, salt_value, digest_value = stored.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    salt = base64.b64decode(salt_value)
    expected = base64.b64decode(digest_value)
    actual = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
    return hmac.compare_digest(actual, expected)


def hash_token(token: str) -> str:
    return hmac.new(settings.jwt_secret.encode(), token.encode(), hashlib.sha256).hexdigest()


def bearer_token(value: str) -> str:
    prefix = "Bearer "
    if not value.startswith(prefix):
        return ""
    return value[len(prefix) :].strip()


def serialize_user(user: dict) -> dict[str, str | int | bool | None]:
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "phone": user["phone"],
        "email_verified": bool(user["email_verified"]),
        "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
    }
