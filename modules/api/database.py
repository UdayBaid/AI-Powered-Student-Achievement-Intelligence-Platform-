from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from modules.api.config import DATABASE_URL

url = make_url(DATABASE_URL)
if url.get_backend_name() == "sqlite" and url.database not in (None, ":memory:"):
    Path(url.database).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)

connect_args = {"check_same_thread": False} if url.get_backend_name() == "sqlite" else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db(database_engine=engine) -> None:
    from modules.api.models import PasswordResetToken, PredictionRecord, User

    Base.metadata.create_all(bind=database_engine)
    user_columns = {
        column["name"]
        for column in inspect(database_engine).get_columns(User.__tablename__)
    }
    if "token_version" not in user_columns:
        with database_engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN token_version "
                "INTEGER NOT NULL DEFAULT 0"
            )
