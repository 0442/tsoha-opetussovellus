from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import db

def validate_credentials(username:str, password:str) -> bool:
    """Returns True if credentials are valid, otherwise False."""

    sql = text("SELECT password FROM users WHERE name = :username AND password = :password")
    result = db.session.execute(sql, {"username":username, "password":password})
    if len(result.all()) == 0:
        return False
    else:
        return True

def get_user_id(username: str) -> str:
    sql = text("SELECT id FROM users WHERE name = :name")
    id = db.session.execute(sql, {"name":username}).fetchone()[0]
    return id

def register_user(username: str, password: str, is_teacher: bool) -> str | None:
    """Returns None if registration was successfull, otherwise an error message."""

    if len(username) < 3:
        return "Username must be at least 3 characters long."
    if len(password) < 3:
        return "Password must be at least 3 characters long."

    role = 1 if is_teacher == True else 0
    sql = text("INSERT INTO users (name, password, role) VALUES (:username, :password, :role)")
    try:
        db.session.execute(sql, {"username":username, "password":password, "role":role})
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
