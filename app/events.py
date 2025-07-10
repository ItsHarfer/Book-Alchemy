"""
app / events.py

Purpose:
SQLAlchemy event handler to enable foreign key support for SQLite connections.
This ensures that foreign key constraints are enforced in SQLite, which is not enabled by default.

Background:
SQLite does not enforce foreign key constraints unless explicitly instructed to do so.
Although tables may define foreign key relations, they will be ignored unless `PRAGMA foreign_keys = ON` is executed for each connection.
This module ensures that behavior by hooking into the SQLAlchemy connection lifecycle.

Features:
- Hooks into SQLAlchemy's Engine "connect" event
- Executes PRAGMA statement to activate foreign key checks on every new connection

Required Modules:
- logging: For logging errors
- sqlalchemy.event: To attach handlers to SQLAlchemy events
- sqlalchemy.engine.Engine: Event target for database connection

Author: Martin Haferanke
Date: 2025-07-11
"""

import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Set up module-level logger
logger = logging.getLogger(__name__)


@event.listens_for(Engine, "connect")
def _enable_sqlite_fk(dbapi_con, con_record):
    """
    Enables SQLite foreign key constraint enforcement for each new connection.

    :param dbapi_con: DBAPI connection object (e.g., sqlite3.Connection).
    :param con_record: SQLAlchemy connection record (unused).
    :raises Exception: If the PRAGMA command fails.
    """
    try:
        dbapi_con.execute("PRAGMA foreign_keys=ON")
    except Exception as exc:
        logger.exception("Failed to enable SQLite foreign keys")
        raise Exception("Could not enforce foreign key constraints for SQLite") from exc
