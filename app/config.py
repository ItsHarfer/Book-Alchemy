import os
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()


class BaseConfig:
    """Base configuration with default settings."""

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-in-production")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    print(os.path.join(os.path.abspath(os.path.dirname(__file__))))

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        # Path relative to config
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/library.sqlite')}",
    )

    processing_image_url = os.getenv("processing_image_url")

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Flask
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration: debug and verbose SQL."""

    DEBUG = True
    SQLALCHEMY_ECHO = False  # Log all SQL statements


class TestingConfig(BaseConfig):
    """Testing configuration: in-memory DB, no API calls."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    # Override AI key to avoid real calls
    OPENAI_API_KEY = None


class ProductionConfig(BaseConfig):
    """Production configuration: read-only optimizations."""

    # Use real database path from environment, fallback to file
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/library.sqlite')}",
    )
    # In production, do not echo SQL
    SQLALCHEMY_ECHO = False


# Mapping for easy lookup
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
