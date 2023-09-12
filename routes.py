from flask import render_template, redirect, request, session

from app import app
from users import valid_credentials, register_user

@app.route("/")
def root():
    return redirect("/courses")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    password = request.form["password"]
    username = request.form["username"]
    if valid_credentials(username, password):
        session["username"] = username
        return redirect("/profile")
    else:
        return render_template("login.html", error_msg="Wrong username or password")

@app.route("/register", methods=["POST"])
def register():
    password = request.form["password"]
    username = request.form["username"]
    err = register_user(username, password)
    if not err:
        session["username"] = username
        return redirect("/profile")
    else:
        return render_template("login.html", error_msg=err)

@app.route("/profile")
def profile():
    user = session["username"]
    if not user:
        return redirect("/login")

    return render_template("profilepage.html")

@app.route("/logout")
def logout():
    session["username"] = None
    return redirect("/")

@app.route("/courses")
def courses():
    return render_template("courses.html")

@app.route("/course/<int:id>")
def course(id):
    return "course " + str(id)