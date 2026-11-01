from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from modules.api.models import User
from modules.api.security import hash_password, verify_password


def normalize_email(email: str) -> str:
    return email.strip().lower()


def create_user(db: Session, *, name: str, email: str, password: str) -> User:
    normalized_email = normalize_email(email)
    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        raise ValueError("An account with this email already exists.")

    user = User(
        name=name.strip(),
        email=normalized_email,
        hashed_password=hash_password(password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("An account with this email already exists.") from exc
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> User | None:
    normalized_email = normalize_email(email)
    user = db.scalar(select(User).where(User.email == normalized_email))
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user
