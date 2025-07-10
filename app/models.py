"""
app / models.py

Purpose:
Defines SQLAlchemy models for Authors and Books used in the library application.
Establishes a one-to-many relationship between authors and their books, including relevant attributes and ORM mapping details.

Features:
- Author model: stores name and lifespan information
- Book model: includes title, ISBN, publication details, and reading status
- Relationship: One Author can have many Books

Required Modules:
- flask_sqlalchemy.SQLAlchemy: For ORM model definition
- sqlalchemy.orm.backref: To define relationship behavior

Exceptions:
- ValueError may occur on invalid data types (e.g., non-date values in `birth_date`)
- SQLAlchemyError may be raised during DB operations (e.g., integrity violations)

Author: Martin Haferanke
Date: 2025-07-11
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref
from sqlalchemy.exc import SQLAlchemyError

# Initialize SQLAlchemy instance
db = SQLAlchemy()


class Author(db.Model):
    """
    SQLAlchemy model representing an author.

    :param id: Primary key (auto-increment integer).
    :param name: Full name of the author (non-nullable).
    :param birth_date: Date of birth of the author (nullable).
    :param date_of_death: Date of death of the author (nullable).
    """

    __tablename__ = "authors"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self) -> str:
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self) -> str:
        return f"{self.name} ({self.birth_date} – {self.date_of_death or 'Present'})"


class Book(db.Model):
    """
    SQLAlchemy model representing a book.

    :param id: Primary key (auto-increment integer).
    :param title: Title of the book (non-nullable).
    :param short_description: Brief description of the book (non-nullable).
    :param publication_year: Year the book was published (non-nullable).
    :param isbn: International Standard Book Number (non-nullable).
    :param author_id: Foreign key to Author.id (nullable, SET NULL on delete).
    :param rating: Optional numeric rating.
    :param is_read: Whether the book has been read (default: False).
    :param progress: Reading progress in percentage (default: 0).
    """

    __tablename__ = "books"

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String, nullable=False)
    short_description: str = db.Column(db.String, nullable=False)
    publication_year: int = db.Column(db.Integer, nullable=False)
    isbn: str = db.Column(db.String, nullable=False)

    author_id: int | None = db.Column(
        db.Integer, db.ForeignKey("authors.id", ondelete="SET NULL"), nullable=True
    )
    rating: int | None = db.Column(db.Integer, nullable=True)

    is_read: bool = db.Column(db.Boolean, nullable=False, default=False)
    progress: int = db.Column(db.Integer, nullable=False, default=0)

    # Define relationship to Author model
    author = db.relationship(
        "Author",
        backref=backref(
            "books",
            lazy=True,
            cascade="all, delete",  # Enables cascading delete behavior
        ),
    )

    def __repr__(self) -> str:
        return f"<Book id={self.id} title='{self.title}'>"

    def __str__(self) -> str:
        return f"'{self.title}' ({self.publication_year}) by Author ID {self.author_id}"
