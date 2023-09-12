from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres@localhost/postgres"
app.secret_key = getenv("SECRET_KEY")
db = SQLAlchemy(app)

from routes import *
