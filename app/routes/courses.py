from flask import render_template, redirect, session, request, abort, url_for

from ..services.courses import *
from ..app import app


@app.route("/courses")
def courses():
    crs = get_all_courses()
    return render_template("courses.html",
                           courses=crs,
                           course_count=len(crs))


@app.route("/courses/search", methods=["POST"])
def course_search():
    user_id = session.get("user_id", -1)

    if user_id != -1 and session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    search_word = request.form.get("search", "")
    own_crs = "my-courses" in request.form
    enrolled = "enrolled-courses" in request.form

    crs = search_courses(search_word, own_crs, enrolled, user_id)

    return render_template("courses.html",
                           courses=crs,
                           course_count=len(crs),
                           search_word=search_word)


@app.route("/courses/<int:course_id>")
def course(course_id: int):
    if "user_id" in session:
        exercises = get_all_course_exercises(course_id, session["user_id"])
    else:
        exercises = []
    return render_template("course-page.html",
                           course=get_course_info(course_id),
                           text_materials=get_all_course_materials(course_id),
                           exercises=exercises,
                           completion_count=count_completed(exercises))


@app.route("/new_course", methods=["GET", "POST"])
def new_course():
    if not is_teacher() and not is_student():
        return redirect(url_for("login"))

    if not is_teacher():
        return redirect(url_for("root"))

    if request.method == "GET":
        return render_template("create-course.html")

    # from here on request is POST and user is teacher...

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    # Validate data
    if len(name) < 3:
        return render_template("create-course.html",
                               error="Name too short (min 3 chars).")
    if len(name) > 200:
        return render_template("create-course.html",
                               error="Name too long (max 200 chars).")
    if len(description) > 200:
        return render_template("create-course.html",
                               error="Description too long (max 200 chars).")
    if len(description) == 0:
        description = f"A new course created by {session['username']}."

    course_id = create_course(name, description, session["user_id"])
    return redirect(url_for("course", course_id = course_id))


@app.route("/courses/<int:course_id>/delete", methods=["POST"])
def remove_course(course_id: int):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not is_teacher():
        return redirect(url_for("root"))

    user_id = session.get("user_id", -1)
    if is_course_teacher(user_id, course_id):
        delete_course(course_id)
    else:
        return render_template("courses.html",
                               error="You can only delete courses owned by you.",
                               course=get_course_info(course_id))

    return redirect(url_for("courses"))


@app.route("/courses/<int:course_id>/edit")
def edit_course(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    return render_template("edit-course.html",
                           course=get_course_info(course_id),
                           text_materials=get_all_course_materials(course_id),
                           exercises=get_all_course_exercises(course_id, session["user_id"]))


@app.route("/courses/<int:course_id>/join", methods=["POST"])
def join_course(course_id: int):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not (is_student() or is_teacher()) or is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    add_user_to_course(session["user_id"], course_id)
    return redirect(url_for("course", course_id=course_id))


@app.route("/courses/<int:course_id>/leave", methods=["POST"])
def leave_course(course_id: int):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not is_student() and not is_teacher():
        return redirect(url_for("root"))

    remove_user_from_course(session["user_id"], course_id)
    return redirect(url_for("course", course_id=course_id))


@app.route("/courses/<int:course_id>/edit/title_and_desc", methods=["POST"])
def course_edit_title_and_desc(course_id: int):
    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    new_name = request.form.get("name", "").strip()
    new_desc = request.form.get("desc", "").strip()

    # Validate data
    if len(new_name) < 3:
        return render_template("edit-course.html", error="Name too short (min 3 chars)",
                               course=get_course_info(course_id))
    if len(new_desc) > 200:
        return render_template("edit-course.html", error="Description too long (max 200 chars)",
                               course=get_course_info(course_id))
    if len(new_desc) == 0:
        new_desc = "This course has no description."

    update_course_name(course_id, new_name)
    update_course_desc(course_id, new_desc)
    return redirect(url_for("edit_course", course_id=course_id))


@app.route("/courses/<int:course_id>/edit/add_exercise", methods=["GET", "POST"])
def course_add_exercise(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    if request.method == "GET":
        return render_template("add-exercise.html", course=get_course_info(course_id))

    # from here on request is POST and user is the course's teacher

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    title = request.form.get("title", "").strip()
    question = request.form.get("question", "").strip()
    answer = request.form.get("answer", "").strip()
    max_points = request.form.get("max-points", "").strip()
    choices = request.form.get("choices", None)

    # Validate data
    if len(title) < 3 or len(question) < 3:
        return render_template("add-exercise.html",
                               error="Text contents too short (min 3 chars)",
                               course=get_course_info(course_id))
    if len(title) > 500 or len(question) > 500 or (choices and len(choices) > 500):
        return render_template("add-exercise.html",
                               error="Text contents too long (max 300 chars)",
                               course=get_course_info(course_id))
    if not 0 < int(max_points) < 999:
        return render_template("add-exercise.html",
                               error="Grading outside of range 0 - 999",
                               course=get_course_info(course_id))

    add_course_exercise(course_id, title, question,
                        answer, max_points, choices)
    return redirect(url_for("edit_course", course_id=course_id))


@app.route("/courses/<int:course_id>/edit/add_material", methods=["GET", "POST"])
def course_add_material(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    if request.method == "GET":
        return render_template("add-course-material.html",
                               course=get_course_info(course_id))

    if session.get("csrf_token", None) != request.form.get("csrf_token", -1):
        abort(403)

    title = request.form.get("title", "")
    text = request.form.get("text", "")

    # Validate data
    if len(title) < 3:
        return render_template("add-course-material.html",
                               error="Title too short (min 3 chars)",
                               course=get_course_info(course_id))
    if len(title) > 500:
        return render_template("add-course-material.html",
                               error="Title too long (max 500 chars)",
                               course=get_course_info(course_id))
    if len(text) < 3:
        return render_template("add-course-material.html",
                               error="Text too short (min 3 chars)",
                               course=get_course_info(course_id))
    if len(text) > 10000:
        return render_template("add-course-material.html",
                               error="Text too long (max 10000 chars)",
                               course=get_course_info(course_id))

    add_course_material(course_id, title, text)
    return redirect(url_for("edit_course", course_id=course_id))


@app.route("/courses/<int:course_id>/exercises/<int:exercise_id>", methods=["GET"])
def course_exercise_page(course_id: int, exercise_id: int):
    if not (is_student() or is_teacher()):
        return redirect(url_for("root"))

    user_id = session.get("user_id", -1)

    if not (is_course_student(user_id, course_id) or is_course_teacher(user_id, course_id)):
        return redirect(url_for("root"))

    exercise = get_course_exercise(exercise_id, user_id, course_id)

    if not exercise:
        return redirect(url_for("course", course_id=course_id))

    if not exercise.choices:
        return render_template("exercise.html",
                               exercise=exercise,
                               course=get_course_info(course_id))

    return render_template("exercise-multichoice.html",
                           exercise=exercise,
                           course=get_course_info(course_id))


@app.route("/courses/<int:course_id>/materials/<int:material_id>", methods=["GET"])
def course_material_page(course_id: int, material_id: int):
    if not (is_student() or is_teacher()):
        return redirect(url_for("root"))

    user_id = session.get("user_id", -1)
    if not (is_course_student(user_id, course_id) or is_course_teacher(user_id, course_id)):
        return redirect(url_for("root"))

    material = get_course_material(course_id, material_id)
    return render_template("material.html", material=material,
                           course=get_course_info(course_id))


@app.route("/courses/<int:course_id>/exercises/<int:exercise_id>/submit", methods=["POST"])
def submit_exercise(course_id: int, exercise_id: int):
    if not is_student():
        return redirect(url_for("root"))

    user_id = session.get("user_id", -1)
    if not is_course_student(user_id, course_id):
        return redirect(url_for("root"))

    answer = request.form.get("answer", "")
    if len(answer) == 0 or len(answer) > 10000:
        abort(400)

    submit_answer(exercise_id, user_id, answer)
    return redirect(url_for("course_exercise_page", course_id=course_id,
                            exercise_id=exercise_id))



@app.route("/courses/<int:course_id>/stats", methods=["GET"])
def course_stats(course_id: int):
    if not is_teacher() or not is_course_teacher(session["user_id"], course_id):
        return redirect(url_for("root"))

    stats = get_all_submissions(course_id)
    crs = get_course_info(course_id)
    participants = get_course_participant_names(course_id)
    return render_template("course-stats.html",
                           course=crs,
                           stats=stats,
                           participants=participants)


@app.route("/courses/<int:course_id>/submissions/<int:submission_id>", methods=["GET", "POST"])
def grading(course_id: int, submission_id: int):
    submission = get_submission(submission_id)
    if not submission:
        abort(404, "Submission does not exist")

    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        grade = request.form.get("grade")
        exercise = get_exercise_by_submission(submission_id)
        if not grade or not 0 <= int(grade) <= exercise.max_points:
            abort(400, "Invalid grade")

        grade_submission(submission_id, grade)
        return redirect(url_for("course_stats"), course_id = course_id)

    return render_template("grading.html",
                           course=get_course_info(course_id),
                           submission=submission)
