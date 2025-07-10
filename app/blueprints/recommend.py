"""
Recommend Blueprint – AI-powered book recommendation endpoints
Handles displaying the recommendation form, generating recommendations via AI,
and adding AI-recommended books to the library.
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import desc

from app.models import db, Book
from ..utils import commit_session, get_or_create_author
from ..services.ai_services import prepare_books_data, fetch_ai_recommendation

logger = logging.getLogger(__name__)

recommend_bp = Blueprint("recommend", __name__, url_prefix="/recommend")


@recommend_bp.route("/", methods=["GET"])
def show_recommend_form():
    """
    Render the recommendation request form.

    :return: Rendered recommend.html template.
    """
    return render_template("recommend.html")


@recommend_bp.route("/", methods=["POST"])
def generate_recommendations():
    """
    Generate 3 book recommendations using AI based on top-rated books.

    :form: none
    :return: Rendered recommend.html with recommendations or error.
    :raises Exception: if AI service fails or no top-rated books.
    """
    top_books = Book.query.filter(Book.rating >= 8).order_by(desc(Book.rating)).all()
    if not top_books:
        return render_template(
            "recommend.html", error="You don't have any books rated above 8 yet."
        )

    try:
        # Prepare data for AI prompt
        data = prepare_books_data(top_books)

        # Gather existing titles to exclude
        existing_titles = [b.title for b in Book.query.all()]

        # Build explicit prompt with exclusion instructions and JSON schema
        prompt = f"""
        Based on these top-rated books, recommend exactly 3 similar titles.
        Exclude any books already in the library: {existing_titles}
        
        
        Return your answer as valid JSON with one top-level key:

        {{
          "recommendations": [
            {{
              "title": "<string>",
              "author": "<string>",
              "author_birth_date": "YYYY-MM-DD",         # empty string if unknown
              "author_date_of_death": "YYYY-MM-DD",      # empty string if still alive or unknown
              "description": "<string, max 2 short sentences>",
              "isbn": "<string>",
              "publication_year": <integer>
            }},
            {{ ... }}, 
            {{ ... }}
          ]
        }}

        Top-rated books to base your recommendations on:
        {json.dumps(data, indent=2)}

        Make sure:
        - The outer object has exactly one field: "recommendations".
        - There are exactly 3 items in the array.
        - Dates use ISO format (YYYY-MM-DD) or an empty string.
        - Descriptions are brief (max. 2 sentences).
        - Try to vary in your book selection to get different recommendations.
        """
        # Call AI service
        result = fetch_ai_recommendation(prompt)
        # Normalize response to list of recommendations
        if isinstance(result, dict):
            recs = result.get("recommendations", [])
        elif isinstance(result, list):
            recs = result
        else:
            logger.error("Unexpected AI response format: %r", result)
            recs = []

        # Filter out already-owned books
        existing = {(b.title, b.author.name) for b in Book.query.all()}
        filtered = [
            r for r in recs if (r.get("title"), r.get("author")) not in existing
        ]

        # If no new suggestions, notify user
        message = None
        if not filtered:
            message = (
                "All recommended books are already in your library. Try again later."
            )

        return render_template(
            "recommend.html",
            recommendations=filtered,
            user_books=top_books,
            error=message,
        )
    except Exception as e:
        logger.exception("Recommendation generation failed")
        return render_template("recommend.html", error=f"An error occurred: {e}")


@recommend_bp.route("/add", methods=["POST"])
def add_recommended_book():
    """
    Add a selected AI-recommended book to the library.

    :form title: Title of the recommended book (required).
    :form author: Author name (required).
    :form birth_date: YYYY-MM-DD (optional).
    :form date_of_death: YYYY-MM-DD (optional).
    :form isbn: ISBN (optional).
    :form description: Short description (optional).
    :form publication_year: Year published (optional).
    :return: JSON with success status and message or error.
    :raises ValueError: if required fields are missing.
    :raises Exception: if database commit fails.
    """
    title = request.form.get("title")
    author_name = request.form.get("author")
    if not title or not author_name:
        return jsonify({"success": False, "error": "Title and author are required."})

    birth = request.form.get("birth_date")
    death = request.form.get("date_of_death")
    pub_year = request.form.get("publication_year")

    try:
        birth_date = datetime.strptime(birth, "%Y-%m-%d").date() if birth else None
        death_date = datetime.strptime(death, "%Y-%m-%d").date() if death else None
    except ValueError as ve:
        logger.error("Invalid date format for recommended book: %s", ve)
        return jsonify({"success": False, "error": "Invalid date format."})

    try:
        publication_year = (
            int(pub_year) if pub_year and pub_year.isdigit() else datetime.now().year
        )
        author = get_or_create_author(author_name, birth_date, death_date)
        if Book.query.filter_by(title=title, author_id=author.id).first():
            return jsonify(
                {"success": False, "error": "This book is already in your library."}
            )

        book = Book(
            isbn=request.form.get("isbn", f"REC-{int(datetime.now().timestamp())}"),
            title=title,
            short_description=request.form.get("description", ""),
            publication_year=publication_year,
            author_id=author.id,
            rating=0,
            is_read=False,
            progress=0,
        )
        db.session.add(book)
        commit_session()
        return jsonify(
            {"success": True, "message": f"'{title}' by {author_name} has been added!"}
        )
    except Exception as e:
        logger.exception("Failed to add recommended book")
        return jsonify({"success": False, "error": "An unexpected error occurred."})
