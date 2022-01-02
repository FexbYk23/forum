from flask import session
from user import get_user_id as get_user_db_id
import secrets

def login_as(username):
    session["username"] = username
    session["user_id"] = get_user_db_id(username)
    session["csrf_token"] = secrets.token_hex(16)

def get_session_user():
    if "username" in session.keys():
        return session["username"]
    return None

def get_user_id():
    if "user_id" in session.keys():
        return session["user_id"]
    return None

def check_csrf_token(token):
    return token == session["csrf_token"]

def end_session():
    del session["username"]
    del session["user_id"]
    del session["csrf_token"]

