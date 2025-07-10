# app / blueprints / books.py
"""
Provides routes for managing books in the application, including CRUD operations,
as well as AJAX endpoints for rating and status updates.

Features:
- Add new books via HTML form
- Edit existing book information and update reading status
- View detailed book information, optionally as modal
- Delete books, including optional deletion of the author if no books remain
- Rate books via AJAX

Dependencies:
- Flask (Blueprint, render_template, request, redirect, url_for, jsonify)
- SQLAlchemy ORM (db, Book, Author)
- Utility: commit_session (wrapper for database commit with error handling)

Raises:
- ValueError: if form data is missing or invalid
- KeyError: if form data keys are missing
- SQLAlchemyError: if database operations fail
- JSONDecodeError: when parsing request payloads fails (where applicable)
- NotFound: if a queried book or author does not exist

Author: Martin Haferanke
Date: 2025-07-10
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import db, Book, Author
from ..utils import commit_session
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("/add", methods=["GET", "POST"])
def add_book():
    """
    Add a new book via form submission.

    :form isbn: ISBN string (optional)
    :form title: Book title (required)
    :form short_description: Brief description (optional)
    :form publication_year: Year published (optional, defaults to current year)
    :form author_id: Existing author ID (required)
    :return: Rendered template or redirect
    :raises ValueError: if required form data is missing or invalid
    :raises SQLAlchemyError: if database commit fails
    """
    message = None
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        isbn = request.form.get("isbn", "")
        title = request.form.get("title")
        desc_text = request.form.get("short_description", "")
        year = request.form.get(
            "publication_year", db.func.strftime("%Y", db.func.date("now"))
        )
        author_id = request.form.get("author_id")

        if not title or not author_id:
            message = "Title and author are required."
        else:
            try:
                book = Book(
                    isbn=isbn,
                    title=title,
                    short_description=desc_text,
                    publication_year=int(year),
                    author_id=int(author_id),
                )
                db.session.add(book)
                commit_session()
                # Replace emoji with ASCII equivalent
                msg = f"+ '{book.title}' added to your library!"
                return redirect(url_for("home.home", message=msg))
            except (ValueError, SQLAlchemyError) as e:
                logger.exception("Failed to add book")
                raise

    if request.args.get("modal") == "true":
        return render_template(
            "partials/add/book.html", authors=authors, message=message
        )

    # Fallback
    return render_template("books/add.html", authors=authors, message=message)


@books_bp.route("/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    """
    Delete a book and its author if no other books remain.

    :param book_id: ID of the book to remove
    :return: Redirect to home
    :raises NotFound: if book does not exist
    :raises SQLAlchemyError: if deletion or commit fails
    """
    book = Book.query.get_or_404(book_id)
    author = book.author
    try:
        db.session.delete(book)
        if not Book.query.filter_by(author_id=author.id).count():
            db.session.delete(author)
        commit_session()
    except SQLAlchemyError:
        logger.exception("Failed to delete book")
        raise
    return redirect(url_for("home.home"))


@books_bp.route("/<int:book_id>", methods=["GET"])
def book_detail(book_id: int):
    """
    Display book details, optionally as modal.

    :param book_id: ID of the book
    :query modal: 'true' for partial/modal rendering
    :return: Rendered template
    :raises NotFound: if book does not exist
    """
    book = Book.query.get_or_404(book_id)
    if request.args.get("modal") == "true":
        return render_template("partials/detail/book.html", book=book)
    return render_template("books/detail.html", book=book)


@books_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id: int):
    """
    Edit book details via form or AJAX.

    :param book_id: ID of the book
    :form title: New title (optional)
    :form author_id: New author ID (optional)
    :form short_description: New description (optional)
    :form rating: New integer rating (optional, 0–10)
    :form is_read: 'on' if read (optional)
    :form progress: Integer 0–100 (optional)
    :return: JSON for AJAX or rendered modal template
    :raises NotFound: if book not found
    :raises SQLAlchemyError: if commit fails
    """
    book = Book.query.get_or_404(book_id)
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        try:
            book.title = request.form.get("title", book.title)
            book.author_id = int(request.form.get("author_id", book.author_id))
            book.short_description = request.form.get(
                "short_description", book.short_description
            )

            rating_str = request.form.get("rating", "").strip()
            if rating_str.isdigit():
                book.rating = max(0, min(10, int(rating_str)))

            book.is_read = request.form.get("is_read") == "on"

            progress_str = request.form.get("progress", "").strip()
            if progress_str.isdigit():
                book.progress = max(0, min(100, int(progress_str)))

            db.session.commit()
            return jsonify({"success": True})
        except (ValueError, SQLAlchemyError):
            logger.exception("Failed to edit book")
            return jsonify({"success": False})

    if request.args.get("modal") == "true":
        return render_template("partials/edit/book.html", book=book, authors=authors)

    # Fallback
    return render_template("books/edit.html", book=book, authors=authors)


@books_bp.route("/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id: int):
    """
    Update a book's rating via AJAX.

    :param book_id: Book ID
    :form rating: Integer rating 0–10
    :return: JSON success flag and new rating
    :raises NotFound: if book not found
    :raises ValueError: if rating invalid
    :raises SQLAlchemyError: if commit fails
    """
    book = Book.query.get_or_404(book_id)
    try:
        book.rating = int(request.form.get("rating", 0))
        commit_session()
        return jsonify({"success": True, "rating": book.rating})
    except (ValueError, SQLAlchemyError):
        logger.exception("Failed to rate book")
        raise
