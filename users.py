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

def register_user(username:str, password:str) -> str | None:
    """Returns None if registration was successfull, otherwise an error message."""

    sql = text("INSERT INTO users (name, password) VALUES (:username, :password)")
    try:
        db.session.execute(sql, {"username":username, "password":password})
        db.session.commit()
    except IntegrityError:
        return f"Username '{username}' is already taken."

    return None
