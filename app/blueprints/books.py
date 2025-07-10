# app/blueprints/books.py

"""
Books Blueprint – CRUD operations and AJAX endpoints for books
Handles creation, deletion, detail view, editing, rating, and status updates of books.
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import db, Book, Author
from ..utils import commit_session

logger = logging.getLogger(__name__)

books_bp = Blueprint("books", __name__, url_prefix="/books")


@books_bp.route("/add", methods=["GET", "POST"])
def add_book():
    """
    Add a new book via form submission.

    :form isbn: ISBN string (optional).
    :form title: Book title (required).
    :form short_description: Brief description (optional).
    :form publication_year: Year published (optional).
    :form author_id: Existing author ID (required).
    :return: Rendered template or redirect.
    :raises ValueError: if required form data missing or invalid.
    :raises Exception: if database commit fails.
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
                # send a toast message via the query string
                msg = f"📗 '{book.title}' added to your library!"
                return redirect(url_for("home.home", message=msg))
            except Exception:
                logger.exception("Failed to add book")
                raise
    if request.args.get("modal") == "true":
        return render_template(
            "partials/add_book_modal.html", authors=authors, message=message
        )
    return render_template("books/add.html", authors=authors, message=message)


@books_bp.route("/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    """
    Delete a book and its author if no other books remain.

    :param book_id: ID of the book to remove.
    :return: Redirect to home.
    :raises NotFound: if book does not exist.
    :raises Exception: if deletion or commit fails.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author
    db.session.delete(book)
    # delete author if no other books
    if not Book.query.filter_by(author_id=author.id).count():
        db.session.delete(author)
    commit_session()
    return redirect(url_for("home.home"))


@books_bp.route("/<int:book_id>", methods=["GET"])
def book_detail(book_id: int):
    """
    Display book details, optionally as modal.

    :param book_id: ID of the book.
    :query modal: 'true' for partial/modal rendering.
    :return: Rendered template.
    :raises NotFound: if book does not exist.
    """
    book = Book.query.get_or_404(book_id)
    if request.args.get("modal") == "true":
        return render_template("partials/book_modal.html", book=book)
    return render_template("books/detail.html", book=book)


@books_bp.route("/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id: int):
    """
    Edit book details via form or AJAX.

    :param book_id: ID of the book.
    :form title: New title (optional).
    :form author_id: New author ID (optional).
    :form short_description: New description (optional).
    :form rating: New integer rating (optional, 0–10).
    :form is_read: 'on' if read (optional).
    :form progress: Integer 0–100 (optional).
    :return: JSON for AJAX or rendered modal template.
    :raises NotFound: if book not found.
    :raises Exception: if commit fails.
    """
    book = Book.query.get_or_404(book_id)
    authors = Author.query.order_by(Author.name).all()

    if request.method == "POST":
        try:
            # Update required/always-present fields
            book.title = request.form.get("title", book.title)
            book.author_id = int(request.form.get("author_id", book.author_id))
            book.short_description = request.form.get(
                "short_description", book.short_description
            )

            # Optional rating (only update if a valid integer 0–10)
            rating_str = request.form.get("rating", "").strip()
            if rating_str.isdigit():
                book.rating = max(0, min(10, int(rating_str)))

            # Read-status toggle
            book.is_read = request.form.get("is_read") == "on"

            # Optional progress (only update if a valid integer 0–100)
            progress_str = request.form.get("progress", "").strip()
            if progress_str.isdigit():
                book.progress = max(0, min(100, int(progress_str)))

            # Commit changes
            db.session.commit()
            return jsonify({"success": True})
        except Exception:
            logger.exception("Failed to edit book")
            return jsonify({"success": False})

    # GET: render the edit form inside a modal
    return render_template("partials/book_edit_modal.html", book=book, authors=authors)


@books_bp.route("/<int:book_id>/rate", methods=["POST"])
def rate_book(book_id: int):
    """
    Update a book's rating via AJAX.

    :param book_id: Book ID.
    :form rating: Integer rating 0-10.
    :return: JSON success flag and new rating.
    :raises NotFound: if book not found.
    :raises ValueError: if rating invalid.
    :raises Exception: if commit fails.
    """
    book = Book.query.get_or_404(book_id)
    try:
        book.rating = int(request.form.get("rating", 0))
        commit_session()
        return jsonify({"success": True, "rating": book.rating})
    except Exception:
        logger.exception("Failed to rate book")
        raise
