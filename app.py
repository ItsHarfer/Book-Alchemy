from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create an instance of the Flask application
app = Flask(__name__)

# Start flask server
if __name__ == '__main__':
    app.run(debug=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/library.sqlite'
    db = SQLAlchemy(app)

