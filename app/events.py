# app/events.py

import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_con, con_record):
    """
    Enable SQLite foreign key enforcement on each new database connection.

    :param dbapi_con: Active DBAPI connection object.
    :param con_record: Connection record (unused).
    :raises Exception: if enabling foreign keys via PRAGMA fails.
    """
    try:
        dbapi_con.execute("PRAGMA foreign_keys=ON")
    except Exception:
        logger.exception("Failed to enable SQLite foreign keys")
        raise
