from flask import render_template, redirect, session, request
from services.courses import *
from app import app

def is_teacher() -> bool:
    """Check whether a request came from someone logged in as a teacher."""
    return ("user_id"    in session and
            "is_teacher" in session and
            session["is_teacher"] == True)

def is_student() -> bool:
    """Check whether a request came from someone logged in as a student."""
    return ("user_id"    in session and
            "is_teacher" in session and
            session["is_teacher"] == False)

@app.route("/courses")
def courses():
    courses = get_all_courses()
    return render_template("courses.html",
                           courses=courses,
                           course_count=len(courses))

@app.route("/courses/search", methods=["POST"])
def course_search():
    if "user_id" not in session:
        return redirect("/")

    name = None
    if "search" in request.form:
        name = request.form["search"]

    my = True if "my-courses" in request.form else False
    enrolled = True if "enrolled-courses" in request.form else False
    courses = search_courses(name, my, enrolled, session["user_id"])
    print(courses)
    return render_template("courses.html",
                           courses=courses,
                           course_count=len(courses))


@app.route("/courses/<int:course_id>")
def course(course_id: int):
    if "user_id" in session:
        exercises = get_course_exercises(course_id, session["user_id"])
    else:
        exercises = []
    return render_template("course-page.html",
                           course=get_course_info(course_id),
                           text_materials=get_course_materials(course_id),
                           exercises=exercises,
                           completion_count=count_completed(exercises))

@app.route("/new_course", methods=["GET", "POST"])
def new_course():
    if not is_teacher():
        return redirect("/")

    if request.method == "GET":
        return render_template("create-course.html")

    name = request.form["name"]
    description = request.form["description"]
    course_id = create_course(name, description, session["user_id"])
    return redirect("/courses/" + str(course_id))


@app.route("/courses/<int:course_id>/delete", methods=["POST"])
def remove_course(course_id: int):
    if not is_teacher():
        return redirect("/")

    if is_course_teacher(session["user_id"], course_id):
        delete_course(course_id)

    return redirect("/courses")


@app.route("/courses/<int:course_id>/edit")
def edit_course(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect("/")

    return render_template("edit-course.html",
                            course=get_course_info(course_id),
                            text_materials=get_course_materials(course_id),
                            exercises=get_course_exercises(course_id, session["user_id"]))


@app.route("/courses/<int:course_id>/join", methods=["POST"])
def join_course(course_id: int):
    if not is_student():
        return redirect("/")

    add_user_to_course(session["user_id"], course_id)
    return redirect("/courses/" + str(course_id))


@app.route("/courses/<int:course_id>/leave", methods=["POST"])
def leave_course(course_id: int):
    if not is_student():
        return redirect("/")

    remove_user_from_course(session["user_id"], course_id)
    return redirect("/courses/" + str(course_id))


@app.route("/courses/<int:course_id>/edit/title_and_desc", methods=["POST"])
def course_edit_title_and_desc(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect("/")

    update_course_name(course_id, request.form["name"])
    update_course_desc(course_id, request.form["desc"])
    return redirect(f"/courses/{course_id}/edit")


@app.route("/courses/<int:course_id>/edit/add_exercise", methods=["GET", "POST"])
def course_add_exercise(course_id: int):
    if not is_teacher() or is_course_teacher(session["user_id"], course_id):
        return redirect("/")

    if request.method == "GET":
        return render_template("add-exercise.html", course=get_course_info(course_id))

    title = request.form["title"]
    question = request.form["question"]
    answer = request.form["answer"]
    choices = request.form["choices"] if "choices" in request.form else None
    add_course_exercise(course_id, title, question, answer, choices)
    return redirect(f"/courses/{course_id}/edit")


@app.route("/courses/<int:course_id>/edit/add_material", methods=["GET", "POST"])
def course_add_material(course_id: int):
    if not is_teacher() or is_course_teacher(session["user_id"], course_id):
        return redirect("/")

    if request.method == "GET":
        return render_template("add-course-material.html", course=get_course_info(course_id))

    title = request.form["title"]
    text = request.form["text"]
    add_course_material(course_id, title, text)
    return redirect(f"/courses/{course_id}/edit")


@app.route("/courses/<int:course_id>/exercises/<int:exercise_id>", methods=["GET"])
def course_exercise_page(course_id: int, exercise_id: int):
    if not (is_student() or is_teacher()):
        return redirect("/")
    # TODO: restrict access to students enrolled in course only.

    exercise = None
    for e in get_course_exercises(course_id, session["user_id"]):
        if e.id == exercise_id:
            exercise = e
            break
    if not e.choices:
        return render_template("exercise.html", exercise=exercise, course=get_course_info(course_id))
    else:
        return render_template("exercise-multichoice.html", exercise=exercise, course=get_course_info(course_id))


@app.route("/courses/<int:course_id>/materials/<int:material_id>", methods=["GET"])
def course_material_page(course_id: int, material_id: int):
    if not (is_student() or is_teacher()):
        return redirect("/")
    # TODO: restrict access to students enrolled in course only.

    material = None
    for m in get_course_materials(course_id):
        if m.id == material_id:
            material = m
            break
    print(material)
    return render_template("material.html", material=material, course=get_course_info(course_id))

@app.route("/courses/<int:course_id>/exercises/<int:exercise_id>/submit", methods=["POST"])
def submit_exercise(course_id: int, exercise_id: int):
    if not is_student():
        return redirect("/")
    # TODO: restrict access to students enrolled in course only.

    submit_answer(exercise_id, session["user_id"], request.form["answer"])
    return redirect("/courses/"+ str(course_id) + "/exercises/" + str(exercise_id))


@app.route("/courses/<int:course_id>/stats", methods=["GET"])
def course_stats(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect("/")

    stats = get_course_stats(course_id)
    course = get_course_info(course_id)
    participants = get_course_participant_names(course_id)
    return render_template("course-stats.html",
                           course = course,
                           stats = stats,
                           participants = participants)

