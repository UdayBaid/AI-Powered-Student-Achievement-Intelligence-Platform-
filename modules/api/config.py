import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

_default_db_path = PROJECT_ROOT / "data" / "studentai.db"
_database_url = os.getenv("DATABASE_URL")
if _database_url:
    _parsed_database_url = make_url(_database_url)
    if (
        _parsed_database_url.get_backend_name() == "sqlite"
        and _parsed_database_url.database
        and not Path(_parsed_database_url.database).is_absolute()
    ):
        _database_path = (PROJECT_ROOT / _parsed_database_url.database).resolve()
        _parsed_database_url = _parsed_database_url.set(
            database=_database_path.as_posix()
        )
    DATABASE_URL = _parsed_database_url.render_as_string(hide_password=False)
else:
    DATABASE_URL = f"sqlite:///{_default_db_path.as_posix()}"
JWT_ACCESS_TOKEN_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "30"))
FRONTEND_ORIGINS = tuple(
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173").rstrip("/")
SMTP_HOST = os.getenv("SMTP_HOST", "").strip()
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "").strip()
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "").strip()


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret) < 32 or secret.lower().startswith("replace-"):
        raise RuntimeError(
            "Set JWT_SECRET in the project .env file to a random value "
            "of at least 32 characters."
        )
    return secret
