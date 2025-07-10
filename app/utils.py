"""
Utility functions for Book Alchemy application.
Provides reusable helpers for date parsing, database commits, and author retrieval.
"""

import logging
from datetime import datetime, date

from app.models import db, Author

logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> date | None:
    """
    Parse a date string in YYYY-MM-DD format into a date object.

    :param date_str: String representing a date, or empty.
    :return: datetime.date object or None if input empty.
    :raises ValueError: if the date_str is not in the correct format.
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        logger.error(f"Invalid date format: '{date_str}'")
        raise


def commit_session() -> bool:
    """
    Commit the current database session, rolling back on failure.

    :return: True if commit succeeded, False otherwise.
    :raises Exception: if a database error occurs during commit.
    """
    try:
        db.session.commit()
        return True
    except Exception:
        logger.exception("Database commit failed")
        db.session.rollback()
        raise


def get_or_create_author(name: str, birth: date | None, death: date | None) -> Author:
    """
    Retrieve an existing Author by name or create a new one.

    :param name: Author's full name.
    :param birth: Birth date or None.
    :param death: Date of death or None.
    :return: Author instance.
    :raises Exception: if flushing to the session fails.
    """
    author = Author.query.filter_by(name=name).first()
    if author:
        return author

    author = Author(name=name, birth_date=birth, date_of_death=death)
    db.session.add(author)
    try:
        db.session.flush()
    except Exception:
        logger.exception("Failed to flush author to session")
        raise
    return author
