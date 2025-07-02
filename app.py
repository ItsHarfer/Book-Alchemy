from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for
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


@app.route("/", methods=["GET"])
def home():
    search_query = request.args.get("search")
    sort_param = request.args.get("sort")

    if search_query:
        books = Book.query.filter(Book.title.ilike(f"%{search_query}%")).all()
        message = (
            f"Results for '{search_query}'"
            if books
            else f"No books found for '{search_query}'."
        )
    else:
        if sort_param == "title":
            books = Book.query.order_by(Book.title).all()
        elif sort_param == "author":
            books = Book.query.join(Author).order_by(Author.name).all()
        else:
            books = Book.query.all()
        message = None

    return render_template("home.html", books=books, message=message)


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
        short_description = request.form["short_description"]
        publication_year = request.form["publication_year"]
        author_id = request.form["author_id"]
        new_book = Book(
            isbn=isbn,
            title=title,
            short_description=short_description,
            publication_year=publication_year,
            author_id=author_id,
        )
        db.session.add(new_book)
        db.session.commit()
        message = "Book added successfully!"
    return render_template("add_book.html", authors=authors, message=message)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    message = f"✅ Book '{book.title}' was successfully deleted."

    # Check if the author has other books in the database, if not, delete it
    remaining_books = Book.query.filter_by(author_id=author.id).count()
    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()
        message += f" Author '{author.name}' was also removed from the library."

    # Redirect back to home
    return redirect(url_for("home", message=message))


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    if request.args.get("modal") == "true":
        return render_template("partials/book_modal.html", book=book)
    return render_template("book_detail.html", book=book)


@app.route("/author/<int:author_id>")
def author_detail(author_id):
    author = Author.query.get_or_404(author_id)
    if request.args.get("modal") == "true":
        return render_template("partials/author_modal.html", author=author)
    return render_template("author_detail.html", author=author)


if __name__ == "__main__":
    app.run(debug=True)
