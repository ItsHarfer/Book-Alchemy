"""
app / __init__.py

Purpose:
Flask application factory for the Book Alchemy project. Configures the application,
initializes extensions, registers Blueprints, and sets up the database.

Features:
- Loads environment variables via `dotenv`
- Configures Flask app using environment-specific settings
- Initializes SQLAlchemy and ensures foreign key constraints (SQLite)
- Registers all application Blueprints
- Automatically creates database tables at startup

Required Modules:
- flask.Flask: Core Flask framework
- dotenv.load_dotenv: For loading .env files
- app.config.config_by_name: Configuration mappings
- app.models.db: SQLAlchemy DB instance
- app.events._enable_sqlite_fk: Import to register the event listener
- Various Blueprint modules

Author: Martin Haferanke
Date: 2025-07-11
"""

from flask import Flask
from dotenv import load_dotenv

from .config import config_by_name
from app.models import db
from .events import _enable_sqlite_fk

from app.extentions import limiter

from .blueprints.home import home_bp
from .blueprints.authors import authors_bp
from .blueprints.books import books_bp
from .blueprints.recommend import recommend_bp

import logging
from logging.handlers import RotatingFileHandler
import os


def create_app(config_name: str = None) -> Flask:
    """
    Factory function for initializing the Book Alchemy Flask app.

    :param config_name: Key of the configuration to use
                        ("development", "testing", "production").
                        Defaults to "default" if None or invalid.
    :return: Configured Flask application instance.
    :raises RuntimeError: If app configuration fails or DB initialization encounters errors.
    """
    # Load .env file if present
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)
    cfg = config_by_name.get(config_name or "default")
    app.config.from_object(cfg)

    # Initialize extensions
    db.init_app(app)

    # Register event listeners (enabling SQLite foreign keys)
    _enable_sqlite_fk

    # Create DB tables in application context
    with app.app_context():
        db.create_all()

    # Configure Flask limiter for AI recommendations
    limiter.init_app(app)

    # Register Blueprints
    app.register_blueprint(home_bp)
    app.register_blueprint(authors_bp, url_prefix="/authors")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(recommend_bp, url_prefix="/recommend")

    # Logging to file

    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "bookalchemy.log")

    # Set up rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=3)
    file_handler.setLevel(logging.INFO)

    # Define log format
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Attach handler to root logger
    logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(logging.INFO)
    return app
