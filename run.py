"""
app / run.py

Purpose:
Entrypoint script for running the Book Alchemy Flask application.
Loads configuration from environment variables, initializes the app, and starts the server.

Features:
- Loads configuration via FLASK_CONFIG environment variable
- Supports custom host and port via FLASK_RUN_HOST and FLASK_RUN_PORT
- Invokes the Flask development server

Required Modules:
- os: For accessing environment variables
- app.create_app: Application factory function from the project package

Exceptions:
- ValueError: If FLASK_RUN_PORT is not a valid integer
- RuntimeError: If Flask app fails to initialize

Author: Martin Haferanke
Date: 2025-07-11
"""

import os
from app import create_app

config_name: str = os.getenv("FLASK_CONFIG", "development")
app = create_app(config_name)


if __name__ == "__main__":
    host: str = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port: int = int(os.getenv("FLASK_RUN_PORT", 5002))

    app.run(host=host, port=port)
