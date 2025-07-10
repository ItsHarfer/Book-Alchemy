"""
AI service for Book Alchemy – handles OpenAI integration and recommendation preparation.
"""

import os
import json
import logging

import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def prepare_books_data(books: List[Any]) -> List[Dict[str, Any]]:
    """
    Serialize a list of Book objects into JSON-ready dictionaries for AI prompts.

    :param books: List of Book model instances.
    :return: List of dicts containing book metadata.
    :raises Exception: if serialization fails.
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

    :param prompt: The user prompt for AI.
    :return: Parsed JSON response from AI.
    :raises EnvironmentError: if OPENAI_API_KEY is not set.
    :raises requests.RequestException: if HTTP request fails.
    :raises ValueError: if JSON response is invalid.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("Missing OPENAI_API_KEY environment variable")
        raise EnvironmentError("OPENAI_API_KEY is required for AI recommendations")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
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

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON from AI: %s", content)
        raise ValueError("Invalid JSON response from AI")
