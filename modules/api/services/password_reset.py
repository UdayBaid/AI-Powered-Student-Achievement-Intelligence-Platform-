import hashlib
import secrets
import smtplib
import ssl
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from urllib.parse import quote

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from modules.api.config import (
    FRONTEND_URL,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
)
from modules.api.models import PasswordResetToken, User
from modules.api.security import hash_password

RESET_TOKEN_MINUTES = 15


class ResetEmailDeliveryError(RuntimeError):
    pass


def email_delivery_configured() -> bool:
    return all((SMTP_HOST, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM_EMAIL))


def _send_reset_email(email: str, reset_url: str) -> None:
    message = EmailMessage()
    message["Subject"] = "Reset your StudentAI password"
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = email
    message.set_content(
        "A password reset was requested for your StudentAI account.\n\n"
        f"Use this one-time link within {RESET_TOKEN_MINUTES} minutes:\n"
        f"{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.ehlo()
            smtp.starttls(context=ssl.create_default_context())
            smtp.ehlo()
            smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise ResetEmailDeliveryError("Password reset email could not be delivered.") from exc


def request_password_reset(db: Session, email: str) -> None:
    normalized_email = email.strip().lower()
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is None:
        return

    now = datetime.now(timezone.utc)
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    raw_token = secrets.token_urlsafe(32)
    reset_token = PasswordResetToken(
        user_id=user.id,
        token_hash=hashlib.sha256(raw_token.encode("utf-8")).hexdigest(),
        expires_at=now + timedelta(minutes=RESET_TOKEN_MINUTES),
    )
    db.add(reset_token)
    db.commit()

    reset_url = f"{FRONTEND_URL}/?reset_token={quote(raw_token, safe='')}"
    try:
        _send_reset_email(user.email, reset_url)
    except ResetEmailDeliveryError:
        db.delete(reset_token)
        db.commit()
        raise


def complete_password_reset(db: Session, *, token: str, new_password: str) -> bool:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    reset_token = db.scalar(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    if reset_token is None or reset_token.used_at is not None:
        return False

    expires_at = reset_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    if expires_at <= now:
        return False

    user = db.get(User, reset_token.user_id)
    if user is None:
        return False

    user.hashed_password = hash_password(new_password)
    user.token_version += 1
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )
    db.commit()
    return True
