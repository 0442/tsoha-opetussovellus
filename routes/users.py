from flask import render_template, redirect, session, request
from users import *
from app import app

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    password = request.form["password"]
    username = request.form["username"]
    if validate_credentials(username, password):
        session["username"] = username
        session["is_teacher"] = is_teacher(username)
        session["user_id"] = get_user_id(username)
        return redirect("/profile")
    else:
        return render_template("login.html", error_msg="Wrong username or password")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    password = request.form["password"]
    username = request.form["username"]
    role = request.form["role"]
    err = register_user(username, password, True if role ==
                        "teacher" else False)
    if not err:
        session["username"] = username
        session["is_teacher"] = is_teacher(username)
        session["user_id"] = get_user_id(username)
        return redirect("/profile")
    else:
        return render_template("register.html", error_msg=err)


@app.route("/profile")
def profile():
    user = session["username"]
    if not user:
        return redirect("/login")

    return render_template("profilepage.html")


@app.route("/logout")
def logout():
    session["username"] = None
    session["is_teacher"] = None
    session["user_id"] = None
    return redirect("/")


@app.route("/delete", methods=["POST"])
def delete():
    username = session["username"]
    delete_user(username)
    return redirect("/logout")