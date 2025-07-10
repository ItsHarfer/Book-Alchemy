# app / blueprints / authors.py

"""
Handles CRUD operations for authors including listing, creation,
detail view, and deletion of author records. Supports both full-page
views and AJAX modal fragments for integration in a dynamic frontend.

Features:
- List all authors alphabetically
- Add new authors via full-page or modal form
- View author details
- Delete authors with confirmation (AJAX support)

Modules:
- flask: routing, rendering, request handling
- app.models: database models (Author)
- app.utils: utility functions for date parsing and DB commit
- sqlalchemy.exc: for database error handling
- werkzeug.exceptions: for standardized HTTP error responses

Exceptions:
- ValueError: raised when parsing dates fails
- SQLAlchemyError: raised during database access errors
- InternalServerError: raised when database or processing errors occur
- NotFound: raised when an author record is not found

Author: Martin Haferanke
Date: 2025-07-10
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import InternalServerError
from app.models import db, Author
from ..utils import parse_date, commit_session

logger = logging.getLogger(__name__)

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


@authors_bp.route("/", methods=["GET"])
def list_authors() -> str:
    """
    Retrieve and list all authors ordered alphabetically by name.

    :return: Rendered HTML template for author list (full-page or modal).
    :raises InternalServerError: If a database error occurs.
    """
    try:
        authors = Author.query.order_by(Author.name).all()
        # Return a modal partial if requested via ?modal=true
        if request.args.get("modal") == "true":
            return render_template("partials/list/author.html", authors=authors)

        # Fallback
        return render_template("authors/list.html", authors=authors)

    except SQLAlchemyError:
        logger.exception("Database error while listing authors")
        raise InternalServerError("Error retrieving authors.")


@authors_bp.route("/add", methods=["GET", "POST"])
def add_author() -> str:
    """
    Handle GET and POST requests for adding a new author.

    GET:
      - If ?modal=true → returns the modal form fragment.
      - Otherwise      → returns the full-page form.

    POST:
      - Validates and adds a new author to the database.
      - If ?modal=true → returns JSON result.
      - Otherwise      → redirects with success message.

    :return: Rendered template or JSON response depending on request.
    :raises InternalServerError: If a validation or database error occurs.
    """
    message = None
    is_modal = request.args.get("modal") == "true"

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_str = request.form.get("birth_date", "").strip()
        death_str = request.form.get("date_of_death", "").strip()

        # Basic validation for required fields
        if not name or not birth_str:
            message = "Name and birth date are required."
            if is_modal:
                return jsonify(success=False, message=message)
        else:
            try:
                # Convert string inputs to date objects
                birth_date = parse_date(birth_str)
                death_date = parse_date(death_str) if death_str else None

                # Create and persist author instance
                author = Author(
                    name=name, birth_date=birth_date, date_of_death=death_date
                )
                db.session.add(author)
                commit_session()

                success_msg = f"✅ Author '{author.name}' added!"
                if is_modal:
                    return jsonify(success=True, message=success_msg)

                # Fallback
                return redirect(url_for("home.home", message=success_msg))

            except (ValueError, SQLAlchemyError):
                logger.exception("Failed to add author")
                message = "Error adding author."
                if is_modal:
                    return jsonify(success=False, message=message)
                raise InternalServerError(message)

    # Return appropriate form based on modal request
    if is_modal:
        return render_template("partials/add/author.html", message=message)
    return render_template("authors/add.html", message=message)


@authors_bp.route("/<int:author_id>", methods=["GET"])
def author_detail(author_id: int) -> str:
    """
    Display details for a specific author.

    :param author_id: ID of the author.
    :query modal: 'true' to render a modal fragment.
    :return: Rendered HTML template (full or modal).
    :raises NotFound: If the author does not exist.
    :raises InternalServerError: If a database error occurs.
    """
    try:
        author = Author.query.get_or_404(author_id)
        if request.args.get("modal") == "true":
            return render_template("partials/detail/author.html", author=author)

        # Fallback
        return render_template("authors/detail.html", author=author)

    except SQLAlchemyError:
        logger.exception("Failed to retrieve author details")
        raise InternalServerError("Error retrieving author details.")


@authors_bp.route("/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id: int) -> str:
    """
    Delete a specific author and all associated records.

    :param author_id: ID of the author to delete.
    :return: Redirect or JSON response depending on modal flag.
    :raises InternalServerError: If a database error occurs.
    """
    try:
        author = Author.query.get_or_404(author_id)
        db.session.delete(author)
        commit_session()

        success_msg = f"✅ Author '{author.name}' deleted."
        if request.args.get("modal") == "true":
            return jsonify(success=True, message=success_msg)

        # Fallback
        return redirect(url_for("home.home", message=success_msg))

    except SQLAlchemyError:
        logger.exception("Failed to delete author")
        error_msg = "Error deleting author."
        if request.args.get("modal") == "true":
            return jsonify(success=False, message=error_msg)

        # Fallback
        raise InternalServerError(error_msg)
