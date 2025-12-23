"""
Database infrastructure for Meridiano application.
Responsible for engine, sessions, and connection lifecycle.
"""

from contextlib import contextmanager
from typing import Iterator
from sqlmodel import Session, SQLModel, create_engine
import config_base as config


# Single database engine for the whole application
engine = create_engine(
    config.DATABASE_URL,
    echo=False,
)


def create_db_and_tables() -> None:
    """Create database tables if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    """Create a new SQLModel session."""
    return Session(engine)


@contextmanager
def get_db_connection() -> Iterator[Session]:
    """Context manager for database sessions."""
    session = get_session()
    try:
        yield session
    finally:
        session.close()