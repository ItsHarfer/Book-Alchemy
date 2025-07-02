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

    # Add books with descriptions
    books = [
        # Harry Potter Series
        Book(
            isbn="9780439554930",
            title="Harry Potter and the Sorcerer's Stone",
            publication_year=1997,
            author_id=1,
            rating=9,
            short_description="A young boy discovers he's a wizard and enters the magical world of Hogwarts for the first time.",
        ),
        Book(
            isbn="9780439064873",
            title="Harry Potter and the Chamber of Secrets",
            publication_year=1998,
            author_id=1,
            rating=9,
            short_description="Harry returns to Hogwarts where a hidden chamber unleashes danger upon the school.",
        ),
        Book(
            isbn="9780439136365",
            title="Harry Potter and the Prisoner of Azkaban",
            publication_year=1999,
            author_id=1,
            rating=9,
            short_description="A mysterious fugitive threatens Hogwarts as Harry uncovers secrets about his past.",
        ),
        Book(
            isbn="9780439139601",
            title="Harry Potter and the Goblet of Fire",
            publication_year=2000,
            author_id=1,
            rating=9,
            short_description="Harry is unexpectedly entered into a deadly magical tournament between schools.",
        ),
        Book(
            isbn="9780439358071",
            title="Harry Potter and the Order of the Phoenix",
            publication_year=2003,
            author_id=1,
            rating=9,
            short_description="As Voldemort rises, Harry battles both the Dark Lord and disbelief from the wizarding world.",
        ),
        Book(
            isbn="9780439785969",
            title="Harry Potter and the Half-Blood Prince",
            publication_year=2005,
            author_id=1,
            rating=9,
            short_description="Harry learns about Voldemort’s past and a hidden weapon while dark forces grow stronger.",
        ),
        Book(
            isbn="9780545010221",
            title="Harry Potter and the Deathly Hallows",
            publication_year=2007,
            author_id=1,
            rating=9,
            short_description="Harry, Ron, and Hermione leave Hogwarts to hunt Horcruxes and face Voldemort in a final battle.",
        ),
        # A Song of Ice and Fire Series
        Book(
            isbn="9780553103540",
            title="A Game of Thrones",
            publication_year=1996,
            author_id=2,
            rating=9,
            short_description="Noble families vie for power in Westeros as dark forces stir beyond the Wall.",
        ),
        Book(
            isbn="9780553108033",
            title="A Clash of Kings",
            publication_year=1998,
            author_id=2,
            rating=9,
            short_description="Multiple kings rise to claim the Iron Throne amid war, betrayal, and shifting alliances.",
        ),
        Book(
            isbn="9780553106633",
            title="A Storm of Swords",
            publication_year=2000,
            author_id=2,
            rating=9,
            short_description="The bloody struggle for power deepens with shocking betrayals and tragic losses.",
        ),
        Book(
            isbn="9780553801477",
            title="A Feast for Crows",
            publication_year=2005,
            author_id=2,
            rating=9,
            short_description="As Westeros reels from war, new factions rise in the aftermath of fractured kingdoms.",
        ),
        Book(
            isbn="9780553801507",
            title="A Dance with Dragons",
            publication_year=2011,
            author_id=2,
            rating=9,
            short_description="While Jon Snow defends the Wall, Daenerys struggles to rule Meereen and claim her destiny.",
        ),
    ]
    db.session.add_all(books)
    db.session.commit()

    print(" Books successfully added to the database.")
