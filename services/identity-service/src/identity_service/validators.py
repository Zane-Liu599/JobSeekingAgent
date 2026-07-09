from __future__ import annotations

import re


def normalize_email(value: str) -> str:
    email = value.lower().strip()
    if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        raise ValueError("Enter a valid email address.")
    return email


def normalize_phone(value: str) -> str:
    phone = re.sub(r"\s+", " ", value.strip())
    if not re.fullmatch(r"\+?[0-9][0-9 ()-]*", phone):
        raise ValueError("Enter a valid phone number.")
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 8 or len(digits) > 15:
        raise ValueError("Phone number must contain 8 to 15 digits.")
    return phone
