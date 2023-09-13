from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from app import db

def valid_credentials(username:str, password:str) -> bool:
    """Returns True if credentials are valid, otherwise False."""

    sql = text("SELECT password FROM users WHERE name = :username AND password = :password")
    result = db.session.execute(sql, {"username":username, "password":password})
    if len(result.all()) == 0:
        return False
    else:
        return True

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