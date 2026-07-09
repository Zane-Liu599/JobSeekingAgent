from __future__ import annotations

from datetime import timedelta

from identity_service.settings import IdentitySettings

settings = IdentitySettings()

EMAIL_VERIFICATION_TTL = timedelta(hours=24)
EMAIL_RESEND_COOLDOWN = timedelta(seconds=60)
SESSION_TTL = timedelta(days=14)
