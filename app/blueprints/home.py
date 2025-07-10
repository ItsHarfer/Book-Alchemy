# app / blueprints / home.py
"""
Provides the main landing page of the application with support for book search,
author filtering, and dynamic sorting of results.

Features:
- Filter books by partial title match
- Filter books by specific author ID
- Sort results by book title or author name
- Display dynamic messages based on filters

Dependencies:
- Flask (Blueprint, render_template, request)
- SQLAlchemy ORM (Book, Author)

Raises:
- SQLAlchemyError: if database query fails
- Exception: for any unexpected error during rendering

Author: Martin Haferanke
Date: 2025-07-10
"""

import logging
from flask import Blueprint, render_template, request
from app.models import Book, Author
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET"])
def home():
    """
    Display the home page with optional filters and sorting.

    :query search: Title substring to search (optional)
    :query author_id: ID of the author to filter by (optional)
    :query sort: Sort by 'title' or 'author' (optional)
    :return: Rendered home page template
    :raises SQLAlchemyError: on database query errors
    :raises Exception: on unexpected errors
    """
    try:
        search_query = request.args.get("search", type=str)
        author_id = request.args.get("author_id", type=int)
        sort_param = request.args.get("sort", type=str)
        message = None

        q = Book.query

        if search_query:
            q = q.filter(Book.title.ilike(f"%{search_query}%"))

        author = None
        if author_id:
            q = q.filter(Book.author_id == author_id)
            author = Author.query.get(author_id)

        if sort_param == "title":
            q = q.order_by(Book.title)
        elif sort_param == "author":
            q = q.join(Author).order_by(Author.name)

        books = q.all()

        # Toast Message
        if search_query and not author_id:
            message = f'Showing results for title: "{search_query}"'
        elif author and not search_query:
            message = f"Showing books by author: {author.name}"
        elif search_query and author:
            message = f'Showing results for "{search_query}" by author: {author.name}'

        authors = Author.query.order_by(Author.name).all()

        return render_template(
            "home.html",
            books=books,
            authors=authors,
            selected_author=author_id,
            selected_sort=sort_param,
            search_query=search_query,
            message=message,
        )

    except SQLAlchemyError:
        logger.exception("Database error during home page rendering")
        raise
    except Exception:
        logger.exception("Failed to load home page")
        raise
