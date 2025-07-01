from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from data_models import db, Author, Book

import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Create an instance of the Flask application
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

# Initialize the app with SQLAlchemy
db.init_app(app)

# Create tables within application context
# with app.app_context():
#     db.create_all()

# Start flask server
if __name__ == "__main__":
    app.run(debug=True)
