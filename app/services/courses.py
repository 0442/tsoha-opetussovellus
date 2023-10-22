from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import db
from typing import NamedTuple, Any
from flask import session

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

class Course(NamedTuple):
    id: str
    name: str
    description: str
    teacher_ids: list[str]
    participant_ids: list[str]

def create_course(name: str, description: str, creator_id: str) -> str:
    """Creates a bare course with only a name and a description without any content or exercises.

    Returns the newly created course's id.
    """

    sql = text("""
        INSERT INTO courses (name, description)
        VALUES (:name, :desc);

        INSERT INTO course_teachers (course_id, user_id)
        VALUES ((SELECT currval('courses_id_seq')), :user_id );

        SELECT currval('courses_id_seq');
    """)

    course_id = db.session.execute(sql, {"name":name, "desc":description, "user_id": creator_id}).fetchone()[0]
    db.session.commit()

    return course_id

def delete_course(course_id: int):
    sql = text("DELETE FROM courses WHERE id = :course_id")
    try:
        db.session.execute(sql, {"course_id":course_id})
    # In case of trying to delete a nonexistent course
    except Exception as e:
        print(e)
    db.session.commit()

def add_course_material(course_id: int, title: str, text_content: str) -> None:
    sql = text("INSERT INTO course_text_materials (course_id, title, content) VALUES (:course_id, :title, :content)")
    db.session.execute(sql, {"course_id":course_id, "title":title, "content":text_content})
    db.session.commit()

def add_course_exercise(course_id: int, title: str, question: str, answer: str, max_points: int, choices: None|str) -> None:
    sql = text("""
        INSERT INTO course_exercises (
            course_id, title, question, correct_answer, choices, max_points
        ) VALUES (
            :course_id, :title, :question, :correct_answer, :choices, :max_points
        )"""
    )

    if choices:
        print("Creating a multichoice exercise")
        choices = choices.strip("; ")
    else:
        print("Creating a text exercise")
        sql = text("""
            INSERT INTO course_exercises (
                course_id, title, question, correct_answer, choices, max_points
            ) VALUES (
                :course_id, :title, :question, :correct_answer, NULL, :max_points
            )"""
        )

    db.session.execute(sql, {"course_id": course_id,
                             "title": title,
                             "question": question,
                             "correct_answer": answer,
                             "choices": choices,
                             "max_points": max_points})
    db.session.commit()

def get_all_submissions(course_id: int):
    sql = text("""
        SELECT u.name AS username, es.id, es.exercise_id, es.user_id,
                      es.answer, es.grade, ce.question, ce.title AS exercise_title,
                      ce.correct_answer, ce.max_points, ce.choices
        FROM exercise_submissions es
        LEFT JOIN users u ON u.id = es.user_id
        LEFT JOIN course_exercises ce ON es.exercise_id = ce.id
        WHERE ce.course_id = :course_id
    """)

    results = db.session.execute(sql, {"course_id": course_id}).fetchall()
    return results

def _get_course_participants(course_id: int):
    sql = text("SELECT user_id FROM course_participants WHERE course_id = :course_id")
    return [row[0] for row in db.session.execute(sql, {"course_id":course_id}).fetchall()]

def _get_course_teachers(course_id: int):
    sql = text("SELECT user_id FROM course_teachers WHERE course_id = :course_id")
    return [row[0] for row in db.session.execute(sql, {"course_id":course_id}).fetchall()]

def get_course_participant_names(course_id: int) -> list[str]:
    sql = text("""
        SELECT u.name
        FROM course_participants cp
        LEFT JOIN users u ON u.id = cp.user_id
        WHERE course_id = :course_id
    """)
    return [row[0] for row in db.session.execute(sql, {"course_id":course_id}).fetchall()]

def get_all_courses() -> list[Course]:
    sql = text("SELECT id, name, description FROM courses")
    courses = db.session.execute(sql).fetchall()

    courses_objects = []
    for course_id, name, desc in courses:
        teacher_ids = _get_course_teachers(course_id)
        participant_ids = _get_course_participants(course_id)
        courses_objects.append(Course(course_id, name, desc, teacher_ids, participant_ids))

    return courses_objects

def search_courses(name: str, my: bool, enrolled: bool, user_id: int) -> list[Course]:
    """Returns a list of matching courses"""

    """
    full_sql:
        SELECT c.id, c.name, c.description
        FROM courses c
        LEFT JOIN course_participants cp ON c.id = cp.course_id
        LEFT JOIN course_teachers ct ON c.id = ct.course_id
        WHERE lower(c.name) LIKE lower(:name) OR lower(c.description) LIKE lower(:name)
        AND cp.user_id = :enrolled_user_id
        AND ct.user_id = :teacher_user_id
        GROUP BY c.id
    """

    base_sql = "SELECT c.id, c.name, c.description FROM courses c "
    if enrolled:
        base_sql += "LEFT JOIN course_participants cp ON c.id = cp.course_id "
    if my:
        base_sql += "LEFT JOIN course_teachers ct ON c.id = ct.course_id "
    if enrolled or my or name:
        base_sql += "WHERE "
    if name:
        base_sql += "lower(c.name) LIKE lower(:name) OR lower(c.description) LIKE lower(:name) "
    if name and (enrolled or my):
        base_sql += "AND "
    if enrolled:
        base_sql += "cp.user_id = :user_id "
    if enrolled and my:
        base_sql += "OR "
    if my:
        base_sql += "ct.user_id = :user_id "

    base_sql += "GROUP BY c.id"

    print(base_sql)
    courses = db.session.execute(text(base_sql), {"user_id":user_id, "name":"%"+name+"%"}).fetchall()

    course_objects = []
    for course_id, name, desc in courses:
        teacher_ids = _get_course_teachers(course_id)
        participant_ids = _get_course_participants(course_id)
        course_objects.append(Course(course_id, name, desc, teacher_ids, participant_ids))

    return course_objects



def is_course_teacher(user_id: int, course_id: int) -> bool:
    """Check wether given user is a teacher in given course"""
    sql = text("SELECT id FROM course_teachers WHERE course_id = :course_id AND user_id = :user_id")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id}).fetchall()
    if len(result) < 1:
        return False
    else:
        return True

def is_course_student(user_id: int, course_id: int) -> bool:
    """Check wether given user is a user enrolled in given course"""
    sql = text("SELECT id FROM course_participants WHERE course_id = :course_id AND user_id = :user_id")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id}).fetchall()
    if len(result) < 1:
        return False
    else:
        return True

def get_course_info(course_id: int) -> Course:
    """Returns None if course with course_id doesn't exist, otherwise return a Course object"""

    sql = text("SELECT name, description FROM courses WHERE id = :course_id")
    result = db.session.execute(sql, {"course_id":course_id}).fetchone()
    if result == None:
        return None

    name, description = result

    teacher_ids = _get_course_teachers(course_id)
    participant_ids = _get_course_participants(course_id)

    return Course(course_id, name, description, teacher_ids, participant_ids)

def add_user_to_course(user_id: int, course_id: int) -> None:
    sql = text("INSERT INTO course_participants (user_id, course_id) VALUES (:user_id, :course_id)")
    try:
        db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
        db.session.commit()
    except IntegrityError:
        pass

def remove_user_from_course(user_id: int, course_id: int) -> None:
    sql = text("DELETE FROM course_participants WHERE user_id = :user_id AND course_id = :course_id")
    db.session.execute(sql, {"user_id":user_id, "course_id":course_id})
    db.session.commit()

class Exercise(NamedTuple):
    id: int
    course_id: int
    title: str
    question: str
    correct_answer: str
    choices: None|list[str]

    user_id: int
    submitted_answer: None|str
    grade: None|int
    max_points: int

def get_course_exercise(exercise_id: int, user_id: int, course_id: int):
    sql = text("""
        SELECT ce.id, ce.title, ce.question, ce.max_points, ce.choices, es.answer, ce.correct_answer, es.grade
        FROM course_exercises ce
        LEFT JOIN (
            SELECT id, exercise_id, user_id, answer, grade
            FROM exercise_submissions
            WHERE user_id = :user_id
        ) es ON ce.id = es.exercise_id
        WHERE ce.id = :exercise_id
    """)
    r = db.session.execute(sql, {"exercise_id": exercise_id, "user_id": user_id}).fetchone()
    id, title, question, max_points, choices, submitted_answer, correct_answer, grade = r
    if choices:
        choices = choices.split(";")
    exc = Exercise(id, course_id, title, question,
                    correct_answer, choices, user_id,
                    submitted_answer, grade, max_points)
    return exc

def get_all_course_exercises(course_id: int, user_id: int) -> list[Exercise]:
    sql = text("""
        SELECT ce.id, ce.title, ce.question, ce.max_points, ce.choices, es.answer, ce.correct_answer, es.grade
        FROM course_exercises ce
        LEFT JOIN (
            SELECT id, exercise_id, user_id, answer, grade
            FROM exercise_submissions
            WHERE user_id = :user_id
        ) es ON ce.id = es.exercise_id
        WHERE course_id = :course_id
    """)
    results = db.session.execute(sql, {"course_id":course_id, "user_id":user_id}).fetchall()
    exercises = []
    for r in results:
        id, title, question, max_points, choices, submitted_answer, correct_answer, grade = r
        if choices:
            choices = choices.split(";")
        exc = Exercise(id, course_id, title, question,
                       correct_answer, choices, user_id,
                       submitted_answer, grade, max_points)
        exercises.append(exc)

    return exercises

def get_exercise_by_submission(submission_id: int):
    sql = text("""
        SELECT ce.id, ce.title, ce.question, ce.max_points, ce.choices, es.answer, ce.correct_answer, es.grade
        FROM course_exercises ce
        JOIN exercise_submissions es ON ce.id = es.exercise_id
        WHERE es.id = :submission_id
    """)
    return db.session.execute(sql, {"submission_id": submission_id}).fetchone()

def count_completed(exercises: list[Exercise]):
    completion_count = 0
    for e in exercises:
        completion_count += 1 if e.submitted_answer != None else 0
    return completion_count

def get_course_material(course_id: int, material_id: int) -> list[str]:
    sql = text("""
        SELECT id, title, content
        FROM course_text_materials
        WHERE course_id = :course_id AND id = :material_id
    """)
    results = db.session.execute(sql, {"course_id": course_id, "material_id": material_id}).fetchone()
    return results

def get_all_course_materials(course_id: int) -> list[str]:
    sql = text("""
        SELECT id, title, content
        FROM course_text_materials
        WHERE course_id = :course_id
    """)
    results = db.session.execute(sql, {"course_id":course_id}).fetchall()
    return results

def update_course_name(course_id: int, new_name: str) -> None:
    sql = text("UPDATE courses SET name = :new_name WHERE id = :course_id")
    db.session.execute(sql, {"new_name":new_name, "course_id":course_id})
    db.session.commit()

def update_course_desc(course_id: int, new_desc: str) -> None:
    sql = text("UPDATE courses SET description = :new_desc WHERE id = :course_id")
    db.session.execute(sql, {"new_desc":new_desc, "course_id":course_id})
    db.session.commit()

def submit_answer(exercise_id:int, user_id: int, answer: str) -> None:
    """ Automatically grades the exercise if it was a multiple choice exercise. """

    # If exercise is an essay exercise (choices IS NULL),
    # sets grade as NULL i.e. doesn't grade the exercise.
    #
    # If the exercise is a multichoice (choices IS NOT NULL),
    # gives full points if answer is correct, otherwise 0.
    sql = """
        INSERT INTO exercise_submissions (
            exercise_id, user_id, answer, grade
        ) VALUES (
            :exercise_id, :user_id, :answer,
            CASE WHEN (SELECT choices FROM course_exercises WHERE id = :exercise_id) IS NOT NULL THEN
                CASE
                    WHEN :answer = (SELECT correct_answer FROM course_exercises WHERE id = :exercise_id) THEN
                        (SELECT max_points FROM course_exercises WHERE id = :exercise_id)
                    ELSE 0
                END
            ELSE
                NULL
            END
        )"""

    try:
        db.session.execute(text(sql), {"exercise_id":exercise_id, "user_id":user_id, "answer":answer})
        db.session.commit()
    except IntegrityError:
        pass


def get_submission(submission_id:int) -> None | Any:
    """Returns an object containing the user's answer, exercise's question and the example answer."""
    sql = text("""
        SELECT es.id, es.exercise_id, es.user_id, u.name AS username,
                      es.answer, es.grade, ce.question,
                      ce.title AS exercise_title, ce.correct_answer, ce.max_points
        FROM exercise_submissions es
        LEFT JOIN course_exercises ce ON es.exercise_id = ce.id
        LEFT JOIN users u ON es.user_id = u.id
        WHERE es.id = :sub_id AND ce.choices IS NULL
    """)

    result = db.session.execute(sql, {"sub_id":submission_id}).fetchone()
    return result


def grade_submission(submission_id:int, grade:int):
    sql = text("""
        UPDATE exercise_submissions SET grade = :grade WHERE id = :sub_id
    """)

    db.session.execute(sql, {"grade":grade, "sub_id":submission_id})
    db.session.commit()

