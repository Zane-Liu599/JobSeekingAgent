from __future__ import annotations

import smtplib
from email.message import EmailMessage
from urllib.parse import quote_plus

from fastapi import HTTPException

from identity_service.config import settings


def build_verification_url(token: str) -> str:
    return f"{settings.app_public_url.rstrip('/')}/verify-email?token={quote_plus(token)}"


def ensure_smtp_configured() -> None:
    if not settings.smtp_host or not settings.smtp_from_email:
        raise HTTPException(
            status_code=503,
            detail="Email verification is not configured. Please set SMTP settings.",
        )


def send_verification_email(email: str, name: str, verification_url: str) -> None:
    subject = "Verify your JobSeekingAgent account"
    body = (
        f"Hi {name},\n\n"
        "Please verify your JobSeekingAgent account by opening this link:\n"
        f"{verification_url}\n\n"
        "This link expires in 24 hours."
    )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(body)
    message.add_alternative(
        f"""
        <html>
          <body>
            <p>Hi {name},</p>
            <p>Please verify your JobSeekingAgent account by opening this link:</p>
            <p><a href="{verification_url}">Verify email address</a></p>
            <p>This link expires in 24 hours.</p>
          </body>
        </html>
        """,
        subtype="html",
    )

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
