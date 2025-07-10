"""
app / config / config.py

Purpose:
Configuration module for different Flask application environments, including development, testing, and production.
Defines base configuration values and environment-specific overrides. This includes database connections, API keys, and runtime flags.

Features:
- Loads environment variables using `dotenv`
- Defines default configuration values
- Supports environment-specific configuration inheritance
- Maps configurations to environment names for easy lookup

Required Modules:
- os: For path operations and environment variable access
- dotenv.load_dotenv: For loading variables from .env file

Exceptions:
- No direct exceptions raised in this module, but improper environment variable settings
  could cause runtime issues elsewhere (e.g., invalid DB URI).

Author: Martin Haferanke
Date: 2025-07-11
"""

import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    """Base configuration with default settings."""

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False

    # Dynamically determine base directory and construct DB URI
    _base_dir: str = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{os.path.join(_base_dir, 'data/library.sqlite')}"
    )

    # Image processing service URL
    processing_image_url: str | None = os.getenv("processing_image_url")

    # OpenAI API
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    # Flask settings
    DEBUG: bool = False
    TESTING: bool = False


class DevelopmentConfig(BaseConfig):
    """Development configuration: enables debug mode."""

    DEBUG: bool = True
    SQLALCHEMY_ECHO: bool = False  # Log all SQL statements if needed


class TestingConfig(BaseConfig):
    """Testing configuration: uses in-memory DB and disables API usage."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    OPENAI_API_KEY: None = None  # Prevent real API calls during tests


class ProductionConfig(BaseConfig):
    """Production configuration: disables debug and optimizes DB usage."""

    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data/library.sqlite')}",
    )
    SQLALCHEMY_ECHO: bool = False  # Disable SQL logging in production


# Mapping for easy lookup by environment name
config_by_name: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
