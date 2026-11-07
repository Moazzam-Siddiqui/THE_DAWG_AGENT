"""Create and open the small database used by the robot."""
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from dawg_agent.config import get_settings


class Base(DeclarativeBase):
    """Parent class for database tables."""
    pass


def make_database_engine():
    """Create the database connection.

    SQLite is a simple file on your computer. Other database URLs can be used
    later when the robot is deployed.
    """
    database_url = get_settings().database_url

    if database_url.startswith("sqlite:///"):
        database_file = database_url.removeprefix("sqlite:///")
        if database_file != ":memory:":
            Path(database_file).parent.mkdir(parents=True, exist_ok=True)

        return create_engine(
            database_url,
            connect_args={"check_same_thread": False},
        )

    return create_engine(database_url, pool_pre_ping=True)


engine = make_database_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db() -> None:
    """Create the database tables if they do not exist yet."""
    from dawg_agent import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
