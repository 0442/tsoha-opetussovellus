from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash
from app import db


def validate_credentials(username: str, password: str) -> bool:
    """Returns True if credentials are valid, otherwise False."""

    sql = text("SELECT password FROM users WHERE name = :username")
    result = db.session.execute(sql, {"username": username}).fetchone()

    if not result:
        return False

    if check_password_hash(result.password, password):
        return True
    else:
        return False


def get_user_id(username: str) -> str:
    sql = text("SELECT id FROM users WHERE name = :name")
    id = db.session.execute(sql, {"name": username}).fetchone()[0]
    return id


def register_user(username: str, password: str, is_teacher: bool) -> str | None:
    """Returns None if registration was successfull, otherwise an error message."""

    if not 3 <= len(username) <= 20:
        return "Username must be 3 to 20 characters long."
    if not 3 <= len(password) <= 20:
        return "Password must be 3 to 20 characters long."

    password_hash = generate_password_hash(password)

    role = 1 if is_teacher == True else 0
    sql = text(
        "INSERT INTO users (name, password, role) VALUES (:username, :password_hash, :role)")
    try:
        db.session.execute(
            sql, {"username": username, "password_hash": password_hash, "role": role})
        db.session.commit()
    except IntegrityError:
        return f"Username '{username}' is already taken."

    return None


def delete_user(username: str):
    sql = text("DELETE FROM users WHERE name = :name")
    db.session.execute(sql, {"name": username})
    db.session.commit()


def is_teacher(username: str) -> bool:
    sql = text("SELECT role FROM users WHERE name = :name")
    result = db.session.execute(sql, {"name": username})
    role = result.fetchone()[0]
    return True if role == 1 else False