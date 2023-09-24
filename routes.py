from flask import render_template, redirect, request, session

from app import app
from users import *
from courses import *


@app.route("/")
def root():
    return redirect("/courses")

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
    err = register_user(username, password, True if role == "teacher" else False)
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

@app.route("/courses")
def courses():
    courses = get_all_courses()
    return render_template("courses.html", courses = courses,
                                           course_count = len(courses))

@app.route("/courses/<int:course_id>")
def course(course_id: int):
    return render_template("course-page.html", course=get_course_info(course_id),
                                               text_materials=get_course_materials(course_id),
                                               exercises=get_course_exercises(course_id))

@app.route("/new_course", methods=["GET", "POST"])
def new_course():
    if session["is_teacher"] != True:
        return redirect("/")

    if request.method == "GET":
        return render_template("create-course.html")

    name = request.form["name"]
    description = request.form["description"]
    course_id = create_course(name, description, session["user_id"])
    return redirect("/courses/" + str(course_id))

@app.route("/courses/<int:course_id>/edit")
def edit_course(course_id: int):
    if session["is_teacher"] == False or not is_course_teacher(session["user_id"], course_id):
        return redirect("/")
    else:
        return render_template("edit-course.html", course=get_course_info(course_id),
                                                   text_materials=get_course_materials(course_id),
                                                   exercises=get_course_exercises(course_id))

@app.route("/courses/<int:course_id>/join", methods=["POST"])
def join_course(course_id: int):
    if not session["username"]:
        return redirect("/")
    else:
        add_user_to_course(session["user_id"], course_id)
        return redirect("/courses/" + str(course_id))

@app.route("/courses/<int:course_id>/leave", methods=["POST"])
def leave_course(course_id: int):
    if not session["username"]:
        return redirect("/")
    else:
        remove_user_from_course(session["user_id"], course_id)
        return redirect("/courses/" + str(course_id))

@app.route("/courses/<int:course_id>/edit/title_and_desc", methods=["POST"])
def course_edit_title_and_desc(course_id: int):
    print(request.form["name"])
    update_course_name(course_id, request.form["name"])
    update_course_desc(course_id, request.form["desc"])
    return redirect(f"/courses/{course_id}/edit")

@app.route("/courses/<int:course_id>/edit/add_exercise", methods=["GET", "POST"])
def course_add_exercise(course_id: int):
    if request.method == "GET":
        return render_template("add-exercise.html", course=get_course_info(course_id))

    title = request.form["title"]
    question = request.form["question"]
    answer = request.form["answer"]
    add_course_exercise(course_id, title, question, answer)
    return redirect(f"/courses/{course_id}/edit")

@app.route("/courses/<int:course_id>/edit/add_material", methods=["GET", "POST"])
def course_add_material(course_id: int):
    if request.method == "GET":
        return render_template("add-course-material.html", course=get_course_info(course_id))

    title = request.form["title"]
    text = request.form["text"]
    add_course_material(course_id, title, text)
    return redirect(f"/courses/{course_id}/edit")
