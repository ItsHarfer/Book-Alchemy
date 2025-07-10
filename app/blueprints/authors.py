# app/blueprints/authors.py

"""
Authors Blueprint – CRUD operations for authors
Handles listing, creation, detail view, and deletion of authors.
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models import db, Author
from ..utils import parse_date, commit_session

logger = logging.getLogger(__name__)

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


# List all authors
@authors_bp.route("/", methods=["GET"])
def list_authors():
    """
    List all authors.

    :return: Rendered authors/author_list_modal.html template with all authors.
    """
    authors = Author.query.order_by(Author.name).all()
    if request.args.get("modal") == "true":
        return render_template("partials/author_list_modal.html", authors=authors)
    return render_template("authors/list.html", authors=authors)


# Add author
@authors_bp.route("/add", methods=["GET", "POST"])
def add_author():
    """
    GET:
      - if ?modal=true → return the modal form fragment
      - else           → return the full-page add.html

    POST:
      - if ?modal=true → return JSON {success:bool, message:str}
      - else           → redirect to home with message
    """
    message = None
    is_modal = request.args.get("modal") == "true"

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        birth_str = request.form.get("birth_date", "").strip()
        death_str = request.form.get("date_of_death", "").strip()

        # Validation
        if not name or not birth_str:
            message = "Name and birth date are required."
            if is_modal:
                return jsonify(success=False, message=message)
        else:
            try:
                birth_date = parse_date(birth_str)
                death_date = parse_date(death_str) if death_str else None

                author = Author(
                    name=name, birth_date=birth_date, date_of_death=death_date
                )
                db.session.add(author)
                commit_session()

                success_msg = f"✅ Author '{author.name}' added!"
                if is_modal:
                    # Return JSON → client will close modal + toast
                    return jsonify(success=True, message=success_msg)
                else:
                    # Full-page fallback → redirect back to home with message
                    return redirect(url_for("home.home", message=success_msg))

            except Exception:
                logger.exception("Failed to add author")
                message = "Error adding author."
                if is_modal:
                    return jsonify(success=False, message=message)

    # GET or POST-with-error
    if is_modal:
        return render_template("partials/add_author_modal.html", message=message)
    return render_template("authors/add.html", message=message)


# Author detail
@authors_bp.route("/<int:author_id>", methods=["GET"])
def author_detail(author_id: int):
    """
    Display author details, optionally in a modal.

    :param author_id: ID of the author.
    :query modal: 'true' for modal partial.
    :return: Rendered template.
    :raises NotFound: if author does not exist.
    """
    author = Author.query.get_or_404(author_id)
    if request.args.get("modal") == "true":
        return render_template("partials/author_modal.html", author=author)
    return render_template("authors/detail.html", author=author)


# Delete author (supports AJAX in-modal deletion)
@authors_bp.route("/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id: int):
    """
    Delete an author and all their books.

    If ?modal=true → return JSON {success:bool, message:str}
    Else          → redirect to authors list page
    """
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    commit_session()

    success_msg = f"✅ Author '{author.name}' deleted."
    if request.args.get("modal") == "true":
        return jsonify(success=True, message=success_msg)

    return redirect(url_for("home.home", message=success_msg))
