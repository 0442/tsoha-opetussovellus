from flask import redirect, url_for

from ..app import app
from ..routes.users import *
from ..routes.courses import *


@app.route("/")
def root():
    return redirect(url_for("courses"))
