from __future__ import annotations

from typing import Annotated

from fastapi import FastAPI, Header, status
from platform_common import service_health

from identity_service.auth_service import (
    current_identity_response,
    login_user,
    register_user,
    resend_user_verification,
    verify_email_token,
)
from identity_service.config import settings
from identity_service.db import init_identity_db
from identity_service.schemas import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyResponse,
)
from identity_service.security import hash_password, password_policy_errors, verify_password
from identity_service.validators import normalize_email, normalize_phone

app = FastAPI(
    title="JobSeekingAgent Identity Service",
    version=settings.service_version,
)


@app.on_event("startup")
def bootstrap_identity_service() -> None:
    init_identity_db()


@app.get("/health")
def health():
    return service_health(settings.service_name, settings.service_version)


@app.post("/auth/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest):
    return register_user(payload)


@app.post("/auth/resend-verification", response_model=ResendVerificationResponse)
def resend_verification(payload: ResendVerificationRequest):
    return resend_user_verification(payload)


@app.post("/auth/login", response_model=AuthResponse)
def login(payload: LoginRequest):
    return login_user(payload)


@app.get("/auth/verify-email", response_model=VerifyResponse)
def verify_email(token: str):
    return verify_email_token(token)


@app.get("/identity/me")
def current_identity(authorization: Annotated[str, Header()] = ""):
    return current_identity_response(authorization)


__all__ = [
    "app",
    "RegisterRequest",
    "LoginRequest",
    "ResendVerificationRequest",
    "RegisterResponse",
    "AuthResponse",
    "VerifyResponse",
    "ResendVerificationResponse",
    "hash_password",
    "verify_password",
    "password_policy_errors",
    "normalize_email",
    "normalize_phone",
]
