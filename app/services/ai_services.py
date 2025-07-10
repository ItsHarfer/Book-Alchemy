# app / services / ai_services.py
"""
Provides AI integration for Book Alchemy by preparing recommendation prompts and
communicating with the OpenAI API to retrieve book suggestions.

Features:
- Serialization of Book model instances for structured AI input
- Robust OpenAI API request handling
- Parses structured JSON responses into application-ready data

Dependencies:
- requests: for HTTP communication with OpenAI API
- os: for accessing environment variables
- logging: for error tracking
- json: for encoding and decoding JSON data
- typing: for type hints

Raises:
- EnvironmentError: if OPENAI_API_KEY is not set
- requests.RequestException: on network issues or non-200 responses
- ValueError: if response is not valid JSON
- Exception: for serialization failures

Author: Martin Haferanke
Date: 2025-07-10
"""

import os
import json
import logging
from typing import List, Dict, Any

import requests

logger = logging.getLogger(__name__)


def prepare_books_data(books: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize a list of Book objects into JSON-ready dictionaries for AI prompts.

    :param books: List of Book model instances
    :return: List of dicts containing book metadata
    :raises Exception: if serialization fails
    """
    data: List[Dict[str, Any]] = []
    for b in books:
        try:
            data.append(
                {
                    "title": b.title,
                    "author": b.author.name,
                    "author_birth_date": (
                        b.author.birth_date.strftime("%Y-%m-%d")
                        if b.author.birth_date
                        else ""
                    ),
                    "author_date_of_death": (
                        b.author.date_of_death.strftime("%Y-%m-%d")
                        if b.author.date_of_death
                        else ""
                    ),
                    "rating": b.rating,
                    "description": b.short_description or "",
                    "isbn": b.isbn or "",
                    "publication_year": str(b.publication_year),
                }
            )
        except Exception:
            logger.exception(
                "Failed to serialize book %s", getattr(b, "title", "<unknown>")
            )
            raise
    return data


def fetch_ai_recommendation(prompt: str) -> Dict[str, Any]:
    """
    Send a prompt to the OpenAI API and parse the JSON response with recommendations.

    :param prompt: The user prompt for AI
    :return: Parsed JSON response from AI
    :raises EnvironmentError: if OPENAI_API_KEY is not set
    :raises requests.RequestException: if HTTP request fails
    :raises ValueError: if JSON response is invalid
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Missing OPENAI_API_KEY environment variable")
        raise EnvironmentError("OPENAI_API_KEY is required for AI recommendations")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful book recommendation assistant. "
                    "Always respond with valid JSON containing exactly 3 book recommendations."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 1500,
        "temperature": 0.7,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except requests.RequestException as e:
        logger.exception("OpenAI API request failed")
        raise
    except json.JSONDecodeError:
        logger.error("Invalid JSON from AI response")
        raise ValueError("Invalid JSON response from AI")
