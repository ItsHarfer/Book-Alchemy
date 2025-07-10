# app/blueprints/home.py

"""
Home Blueprint – main landing page with search and sorting functionality.
Handles displaying all books, filtering by title, and ordering by title or author.
"""
import logging
from flask import Blueprint, render_template, request

from app.models import Book, Author

logger = logging.getLogger(__name__)

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET"])
def home():
    """
    Display the home page with:
      - title substring search (&search=…)
      - author filter (&author_id=…)
      - sorting by title or author (&sort=title|author)
    """
    try:
        # 1) Grab query params
        search_query = request.args.get("search", type=str)
        author_id = request.args.get("author_id", type=int)
        sort_param = request.args.get("sort", type=str)
        message = None

        # 2) Build base query
        q = Book.query

        # 3) Title search
        if search_query:
            q = q.filter(Book.title.ilike(f"%{search_query}%"))

        # 4) Author filter
        author = None
        if author_id:
            q = q.filter(Book.author_id == author_id)
            author = Author.query.get(author_id)  # may be None if deleted

        # 5) Sorting
        if sort_param == "title":
            q = q.order_by(Book.title)
        elif sort_param == "author":
            q = q.join(Author).order_by(Author.name)

        # 6) Execute
        books = q.all()

        # 7) Build toast message *only* if author exists
        if search_query and not author_id:
            message = f"Showing results for title: “{search_query}”"
        elif author and not search_query:
            message = f"Showing books by author: {author.name}"
        elif search_query and author:
            message = f"Showing results for “{search_query}” by author: {author.name}"

        # 8) Load all authors for the dropdown
        authors = Author.query.order_by(Author.name).all()

        # 9) Render
        return render_template(
            "home.html",
            books=books,
            authors=authors,
            selected_author=author_id,
            selected_sort=sort_param,
            search_query=search_query,
            message=message,
        )

    except Exception:
        logger.exception("Failed to load home page")
        raise
