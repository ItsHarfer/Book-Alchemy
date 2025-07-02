from datetime import datetime

from flask import Flask, render_template, request
import os

from data_models import db, Author, Book

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    sort = request.args.get("sort", "title")  # Default = 'title'

    if sort == "title":
        books = Book.query.order_by(Book.title).all()
    elif sort == "author":
        books = db.session.query(Book).join(Author).order_by(Author.name).all()
    else:
        books = Book.query.all()

    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    message = ""
    if request.method == "POST":
        name = request.form["name"]
        birth_date = datetime.strptime(request.form["birth_date"], "%Y-%m-%d").date()
        date_of_death = request.form["date_of_death"]
        if date_of_death:
            date_of_death = datetime.strptime(date_of_death, "%Y-%m-%d").date()
        else:
            date_of_death = None
        new_author = Author(
            name=name, birth_date=birth_date, date_of_death=date_of_death
        )
        db.session.add(new_author)
        db.session.commit()
        message = "Author added successfully!"
    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.all()
    message = ""
    if request.method == "POST":
        isbn = request.form["isbn"]
        title = request.form["title"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]
        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=publication_year,
            author_id=author_id,
        )
        db.session.add(new_book)
        db.session.commit()
        message = "Book added successfully!"
    return render_template("add_book.html", authors=authors, message=message)


if __name__ == "__main__":
    app.run(debug=True)
