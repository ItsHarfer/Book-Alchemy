"""
app / extensions.py

Purpose:
Defines and exports shared Flask extensions used throughout the Book Alchemy application.
This file handles delayed (lazy) initialization to avoid circular imports.

Features:
- Centralized declaration of the Flask-Limiter instance
- Configured to use the remote address (IP) as the unique request identity key

Required Modules:
- flask_limiter.Limiter: Core rate limiter class for Flask
- flask_limiter.util.get_remote_address: Default IP-based key function for rate limiting

Author: Martin Haferanke
Date: 2025-07-11
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
