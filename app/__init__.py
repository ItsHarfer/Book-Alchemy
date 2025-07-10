# app/__init__.py

from flask import Flask
from dotenv import load_dotenv

from .config import config_by_name
from app.models import db
from .events import _enable_sqlite_fk

# Blueprints
from .blueprints.home import home_bp
from .blueprints.authors import authors_bp
from .blueprints.books import books_bp
from .blueprints.recommend import recommend_bp


def create_app(config_name: str = None) -> Flask:
    """
    App factory for the Book Alchemy Flask application.

    :param config_name: Key of the configuration to use
                        (one of 'development', 'testing', 'production').
                        Defaults to 'default' if None or invalid.
    :return: Configured Flask application.
    """
    # Load .env early
    load_dotenv()

    app = Flask(__name__, instance_relative_config=False)
    cfg = config_by_name.get(config_name or "default")
    app.config.from_object(cfg)

    # Initialize extensions
    db.init_app(app)

    # Ensure SQLite foreign‐keys are enabled
    # (the decorated listener in events.py will be registered automatically)
    _enable_sqlite_fk  # just import to register the listener

    # Create DB tables if not exist
    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(home_bp)  # routes in home.py
    app.register_blueprint(authors_bp, url_prefix="/authors")
    app.register_blueprint(books_bp, url_prefix="/books")
    app.register_blueprint(recommend_bp, url_prefix="/recommend")

    return app
