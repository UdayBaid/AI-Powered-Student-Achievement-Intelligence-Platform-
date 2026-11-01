from datetime import datetime, timedelta, timezone
from argon2.exceptions import VerificationError, InvalidHashError
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from modules.api.config import JWT_ACCESS_TOKEN_MINUTES, get_jwt_secret

ALGORITHM = "HS256"
_password_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return _password_hasher.verify(hashed_password, password)
    except (VerificationError, InvalidHashError):
        return False


def create_access_token(user_id: int, token_version: int = 0) -> tuple[str, int]:
    expires_in = JWT_ACCESS_TOKEN_MINUTES * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "ver": token_version,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    token = jwt.encode(payload, get_jwt_secret(), algorithm=ALGORITHM)
    return token, expires_in


def decode_access_token(token: str) -> dict[str, object]:
    return jwt.decode(
        token,
        get_jwt_secret(),
        algorithms=[ALGORITHM],
        options={"require": ["exp", "sub", "ver"]},
    )
