from datetime import date
from app import app
from data_models import db, Author, Book

with app.app_context():
    db.drop_all()
    db.create_all()

    # Add authors
    authors = [
        Author(name="J.K. Rowling", birth_date=date(1965, 7, 31)),
        Author(name="George R. R. Martin", birth_date=date(1948, 9, 20)),
    ]
    db.session.add_all(authors)
    db.session.commit()

    # Add books
    books = [
        # Harry Potter Series
        Book(
            isbn="9780439554930",
            title="Harry Potter and the Sorcerer's Stone",
            publication_year=1997,
            author_id=1,
        ),
        Book(
            isbn="9780439064873",
            title="Harry Potter and the Chamber of Secrets",
            publication_year=1998,
            author_id=1,
        ),
        Book(
            isbn="9780439136365",
            title="Harry Potter and the Prisoner of Azkaban",
            publication_year=1999,
            author_id=1,
        ),
        Book(
            isbn="9780439139601",
            title="Harry Potter and the Goblet of Fire",
            publication_year=2000,
            author_id=1,
        ),
        Book(
            isbn="9780439358071",
            title="Harry Potter and the Order of the Phoenix",
            publication_year=2003,
            author_id=1,
        ),
        Book(
            isbn="9780439785969",
            title="Harry Potter and the Half-Blood Prince",
            publication_year=2005,
            author_id=1,
        ),
        Book(
            isbn="9780545010221",
            title="Harry Potter and the Deathly Hallows",
            publication_year=2007,
            author_id=1,
        ),
        # A Song of Ice and Fire Series
        Book(
            isbn="9780553103540",
            title="A Game of Thrones",
            publication_year=1996,
            author_id=2,
        ),
        Book(
            isbn="9780553108033",
            title="A Clash of Kings",
            publication_year=1998,
            author_id=2,
        ),
        Book(
            isbn="9780553106633",
            title="A Storm of Swords",
            publication_year=2000,
            author_id=2,
        ),
        Book(
            isbn="9780553801477",
            title="A Feast for Crows",
            publication_year=2005,
            author_id=2,
        ),
        Book(
            isbn="9780553801507",
            title="A Dance with Dragons",
            publication_year=2011,
            author_id=2,
        ),
    ]
    db.session.add_all(books)
    db.session.commit()

    print("📚 Books successfully added to the database.")
