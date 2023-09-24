from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import db
from typing import NamedTuple

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
    sql_insert_course = text("INSERT INTO courses (name, description) VALUES (:name, :desc)")
    sql_get_id  = text("SELECT currval('courses_id_seq')")
    sql_insert_teacher = text("INSERT INTO course_teachers (course_id, user_id) VALUES (:course_id, :user_id)")

    db.session.execute(sql_insert_course, {"name":name, "desc":description})
    course_id = db.session.execute(sql_get_id).fetchone()[0]
    db.session.execute(sql_insert_teacher, {"course_id":course_id, "user_id":creator_id})

    db.session.commit()
    return course_id

def add_course_material(course_id: int, title: str, text_content: str) -> None:
    sql = text("INSERT INTO course_text_materials (course_id, title, content) VALUES (:course_id, :title, :content)")
    db.session.execute(sql, {"course_id":course_id, "title":title, "content":text_content})
    db.session.commit()

def add_course_exercise(course_id: int, title: str, question: str, answer: str) -> None:
    sql = text("INSERT INTO course_exercises (course_id, title, question, correct_answer) VALUES (:course_id, :title, :question, :correct_answer)")
    db.session.execute(sql, {"course_id":course_id, "title":title, "question":question, "correct_answer":answer})
    db.session.commit()

def _get_course_participants(course_id: int):
    sql = text("SELECT user_id FROM course_participants WHERE course_id = :course_id")
    return [row[0] for row in db.session.execute(sql, {"course_id":course_id}).fetchall()]
def _get_course_teachers(course_id: int):
    sql = text("SELECT user_id FROM course_teachers WHERE course_id = :course_id")
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

def is_course_teacher(user_id: int, course_id: int) -> bool:
    """Check wether given user is a teacher in given course"""
    sql = text("SELECT id FROM course_teachers WHERE course_id = :course_id AND user_id = :user_id")
    result = db.session.execute(sql, {"course_id":course_id, "user_id":user_id})
    if len(result.fetchall()) < 1:
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

def get_course_exercises(course_id: int) -> list[Exercise]:
    sql = text("SELECT id, title, question, correct_answer FROM course_exercises WHERE course_id = :course_id")
    results = db.session.execute(sql, {"course_id":course_id}).fetchall()
    exercises = []
    for r in results:
        id, title, question, correct_answer = r
        exercises.append(Exercise(id, course_id, title, question, correct_answer))
    return exercises

class CourseMaterial(NamedTuple):
    id: int
    course_id: int
    title: str
    content: str

def get_course_materials(course_id: int) -> list[str]:
    sql = text("SELECT id, title, content FROM course_text_materials WHERE course_id = :course_id")
    results = db.session.execute(sql, {"course_id":course_id}).fetchall()
    materials = []
    print(results)
    for r in results:
        id, title, content = r
        materials.append(CourseMaterial(id, course_id, title, content))
    return materials


def update_course_name(course_id: int, new_name: str) -> None:
    sql = text("UPDATE courses SET name = :new_name WHERE id = :course_id")
    db.session.execute(sql, {"new_name":new_name, "course_id":course_id})
    db.session.commit()

def update_course_desc(course_id: int, new_desc: str) -> None:
    sql = text("UPDATE courses SET description = :new_desc WHERE id = :course_id")
    db.session.execute(sql, {"new_desc":new_desc, "course_id":course_id})
    db.session.commit()

def submit_answer(exercise_id:int, user_id: int, answer: str) -> None:
    sql = text("INSERT INTO exercise_submissions (exercise_id, user_id, answer) VALUES (:exercise_id, :user_id, :answer)")
    try:
        db.session.execute(sql, {"exercise_id":exercise_id, "user_id":user_id, "answer":answer})
        db.session.commit()
    except IntegrityError:
        pass