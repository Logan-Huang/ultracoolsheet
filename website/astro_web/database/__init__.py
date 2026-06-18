"""Database module for Astrodbkit database interactions."""

from contextlib import contextmanager
from astrodbkit.astrodb import Database
from astro_web.config import (
    CONNECTION_STRING,
    FOREIGN_KEY,
    LOOKUP_TABLES,
    PRIMARY_TABLE,
    SCHEMA,
    SOURCE_COLUMN,
)


@contextmanager
def get_db():
    """
    Context manager for astrodbkit Database connections.
    Ensures the database session is closed and engine is disposed.
    """
    db = Database(
        CONNECTION_STRING,
        primary_table=PRIMARY_TABLE,
        primary_table_key=SOURCE_COLUMN,
        lookup_tables=LOOKUP_TABLES,
        schema=SCHEMA,
        foreign_key=FOREIGN_KEY,
    )
    try:
        yield db
    finally:
        # Close the session and dispose the engine to release the database file
        if hasattr(db, "session") and db.session:
            db.session.close()
        if hasattr(db, "engine") and db.engine:
            db.engine.dispose()


__all__ = ["sources", "query", "get_db"]
