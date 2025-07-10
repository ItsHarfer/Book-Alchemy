"""
app / utils.py

Purpose:
Utility module for the Book Alchemy application.
Provides common helper functions for parsing dates, handling database commits,
and retrieving or creating authors.

Features:
- Parses ISO-format date strings into Python date objects
- Commits SQLAlchemy sessions with rollback and logging on failure
- Retrieves or creates Author entries safely and efficiently

Required Modules:
- logging: For structured error logging
- datetime: For date and time parsing
- app.models.db: SQLAlchemy database session instance
- app.models.Author: ORM model used in author lookup/creation

Exceptions:
- ValueError: Raised on incorrect date string format in `parse_date`
- SQLAlchemyError: Raised during DB commit or flush operations

Author: Martin Haferanke
Date: 2025-07-11
"""

import logging
from datetime import datetime, date

from sqlalchemy.exc import SQLAlchemyError

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
    :raises SQLAlchemyError: if a database error occurs during commit.
    """
    try:
        db.session.commit()
        return True
    except SQLAlchemyError as e:
        logger.exception(f"Database commit failed: {e}")
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
    except SQLAlchemyError as e:
        logger.exception(f"Failed to flush author to session: {e}")
        raise
    return author
