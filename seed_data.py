from datetime import date
from app import app
from data_models import db, Author, Book

with app.app_context():
    db.drop_all()
    db.create_all()

    # Autoren mit echten date-Objekten
    authors = [
        Author(
            name="Jane Austen",
            birth_date=date(1775, 12, 16),
            date_of_death=date(1817, 7, 18),
        ),
        Author(
            name="George Orwell",
            birth_date=date(1903, 6, 25),
            date_of_death=date(1950, 1, 21),
        ),
        Author(name="J.K. Rowling", birth_date=date(1965, 7, 31), date_of_death=None),
        Author(
            name="F. Scott Fitzgerald",
            birth_date=date(1896, 9, 24),
            date_of_death=date(1940, 12, 21),
        ),
        Author(
            name="Toni Morrison",
            birth_date=date(1931, 2, 18),
            date_of_death=date(2019, 8, 5),
        ),
    ]
    db.session.add_all(authors)
    db.session.commit()

    # Books to add
    books = [
        Book(
            isbn="9780141439518",
            title="Pride and Prejudice",
            publication_year=1813,
            author_id=1,
        ),
        Book(isbn="9780451524935", title="1984", publication_year=1949, author_id=2),
        Book(
            isbn="9780439554930",
            title="Harry Potter and the Sorcerer's Stone",
            publication_year=1997,
            author_id=3,
        ),
        Book(
            isbn="9780743273565",
            title="The Great Gatsby",
            publication_year=1925,
            author_id=4,
        ),
        Book(isbn="9781400033416", title="Beloved", publication_year=1987, author_id=5),
    ]
    db.session.add_all(books)
    db.session.commit()

    print("📚 Data successfully added to the database.")
