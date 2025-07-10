from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import backref

db = SQLAlchemy()


class Author(db.Model):
    """
    A model representing an author.

    :param id: Auto-incrementing primary key.
    :param name: Full name of the author.
    :param birth_date: Author's date of birth.
    :param date_of_death: Author's date of death (nullable).
    """

    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    birth_date = db.Column(db.Date, nullable=True)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author id={self.id} name='{self.name}'>"

    def __str__(self):
        return f"{self.name} ({self.birth_date} – {self.date_of_death or 'Present'})"


class Book(db.Model):
    """
    A model representing a book.

    :param id: Auto-incrementing primary key.
    :param isbn: International Standard Book Number.
    :param title: Title of the book.
    :param short_description: Short description of the book.
    :param publication_year: Year the book was published.
    :param author_id: Foreign key linking to the author of the book.
    """

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    short_description = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    isbn = db.Column(db.String, nullable=False)

    author_id = db.Column(
        db.Integer, db.ForeignKey("authors.id", ondelete="SET NULL"), nullable=True
    )
    rating = db.Column(db.Integer, nullable=True)

    is_read = db.Column(db.Boolean, nullable=False, default=False)
    progress = db.Column(db.Integer, nullable=False, default=0)

    # Connection to Author
    author = db.relationship(
        "Author",
        backref=backref(
            "books",
            lazy=True,
            cascade="all, delete",  # activate ORM cascade
        ),
    )

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}'>"

    def __str__(self):
        return f"'{self.title}' ({self.publication_year}) by Author ID {self.author_id}"
