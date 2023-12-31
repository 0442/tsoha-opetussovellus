import secrets
from flask import render_template, redirect, session, request, abort

from ..app import app
from ..services.users import *


def logout_user():
    del session["username"]
    del session["is_teacher"]
    del session["user_id"]
    del session["csrf_token"]


def login_user(username: str):
    session["username"] = username
    session["user_id"] = get_user_id(username)
    session["is_teacher"] = is_teacher(username)
    session["csrf_token"] = secrets.token_hex(16)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    password = request.form["password"]
    username = request.form["username"]

    if validate_credentials(username, password):
        login_user(username)
        return redirect("/profile")

    return render_template("login.html", error_msg="Wrong username or password")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    password = request.form["password"]
    username = request.form["username"]
    role = request.form["role"]
    err = register_user(username,
                        password,
                        role == "teacher")
    if not err:
        login_user(username)
        return redirect("/profile")

    return render_template("register.html", error_msg=err)


@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("profilepage.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    if "user_id" not in session:
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    delete_user(session["user_id"])
    logout_user()
    return redirect("/")
