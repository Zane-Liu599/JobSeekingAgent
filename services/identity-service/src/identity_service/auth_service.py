from __future__ import annotations

import secrets
import smtplib

import pymysql
from fastapi import HTTPException

from identity_service.config import EMAIL_RESEND_COOLDOWN
from identity_service.emailer import (
    build_verification_url,
    ensure_smtp_configured,
    send_verification_email,
)
from identity_service.repository import (
    cleanup_expired_unverified_user,
    create_session,
    create_user_with_verification_token,
    delete_user,
    get_user_by_email,
    get_user_from_session,
    get_verification_record,
    latest_pending_token_created_at,
    mark_verification_token_used,
    resend_verification_token,
    verify_user_email,
)
from identity_service.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyResponse,
)
from identity_service.security import (
    bearer_token,
    hash_password,
    password_policy_errors,
    serialize_user,
    verify_password,
)
from identity_service.time_utils import utc_now


def register_user(payload: RegisterRequest) -> RegisterResponse:
    errors = password_policy_errors(payload.password)
    if errors:
        raise HTTPException(status_code=422, detail={"password": errors})

    ensure_smtp_configured()
    email = payload.email.lower().strip()
    cleanup_expired_unverified_user(email)
    token = secrets.token_urlsafe(32)
    verification_url = build_verification_url(token)
    user_id: int | None = None

    try:
        user_id = create_user_with_verification_token(
            name=payload.name.strip(),
            email=email,
            phone=payload.phone.strip(),
            password_hash=hash_password(payload.password),
            token=token,
        )
    except pymysql.err.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        ) from exc

    try:
        send_verification_email(email, payload.name.strip(), verification_url)
    except (OSError, smtplib.SMTPException) as exc:
        if user_id:
            delete_user(user_id)
        raise HTTPException(
            status_code=502,
            detail="Could not send verification email. Please try again later.",
        ) from exc

    return RegisterResponse(
        message="Registration created. Please verify your email before logging in.",
        email=email,
    )


def resend_user_verification(payload: ResendVerificationRequest) -> ResendVerificationResponse:
    ensure_smtp_configured()
    email = payload.email.lower().strip()
    cleanup_expired_unverified_user(email)
    user = get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="No pending registration found.")
    if user["email_verified"]:
        raise HTTPException(status_code=409, detail="This email is already verified.")

    enforce_resend_cooldown(user["id"])

    token = secrets.token_urlsafe(32)
    verification_url = build_verification_url(token)
    token_id = resend_verification_token(user["id"], token)

    try:
        send_verification_email(email, user["name"], verification_url)
    except (OSError, smtplib.SMTPException) as exc:
        mark_verification_token_used(token_id)
        raise HTTPException(
            status_code=502,
            detail="Could not send verification email. Please try again later.",
        ) from exc

    return ResendVerificationResponse(
        message="Verification email resent. Please check your inbox.",
        email=email,
    )


def enforce_resend_cooldown(user_id: int) -> None:
    latest_created_at = latest_pending_token_created_at(user_id)
    now = utc_now().replace(tzinfo=None)
    if latest_created_at and latest_created_at + EMAIL_RESEND_COOLDOWN > now:
        retry_after = int((latest_created_at + EMAIL_RESEND_COOLDOWN - now).total_seconds())
        raise HTTPException(
            status_code=429,
            detail=f"Please wait {max(retry_after, 1)} seconds before resending.",
        )


def login_user(payload: LoginRequest) -> AuthResponse:
    email = payload.email.lower().strip()
    cleanup_expired_unverified_user(email)
    user = get_user_by_email(email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user["email_verified"]:
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in.",
        )

    token = secrets.token_urlsafe(40)
    create_session(user["id"], token)
    return AuthResponse(access_token=token, user=serialize_user(user))


def verify_email_token(token: str) -> VerifyResponse:
    record = get_verification_record(token)
    now = utc_now().replace(tzinfo=None)
    if not record:
        raise HTTPException(status_code=404, detail="Verification link is invalid.")
    if record["used_at"] or record["email_verified"]:
        return VerifyResponse(verified=True, message="Email is already verified.")
    if record["expires_at"] < now:
        delete_user(record["user_id"])
        raise HTTPException(status_code=410, detail="Verification link has expired.")

    verify_user_email(record["user_id"], record["id"])
    return VerifyResponse(verified=True, message="Email verified successfully.")


def current_identity_response(authorization: str) -> dict:
    token = bearer_token(authorization)
    if not token:
        return {"authenticated": False}
    user = get_user_from_session(token)
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": serialize_user(user)}
