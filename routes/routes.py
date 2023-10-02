from flask import redirect
from app import app
from routes.users import *
from routes.courses import *

@app.route("/")
def root():
    return redirect("/courses")
