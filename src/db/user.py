from werkzeug.security import check_password_hash, generate_password_hash
from db.db import db


def does_user_exist(username):
    sql = "SELECT COUNT(*) FROM users WHERE name = :username"
    result = db.session.execute(sql, {"username":username}).fetchone()
    print(result)
    return result[0] != 0

def get_user_id(username):
    sql = "SELECT id FROM users WHERE name = :username"
    result = db.session.execute(sql, {"username":username}).fetchone()
    if result == None:
        return None
    return result[0]

def get_user_list():
    sql = "SELECT id,name FROM users"
    result = db.session.execute(sql).fetchall()
    return {x[0]:x[1] for x in result}

def check_user_credentials(username, password_hash):
    sql = "SELECT password_hash FROM users WHERE name=:username"
    result = db.session.execute(sql, {"username":username}).fetchone()
    if result == None: # User not found
        return False
    return check_password_hash(result[0], password_hash)

def add_user(user, password_hash):
    sql = "INSERT INTO users VALUES (DEFAULT, :username, :password, false)"
    db.session.execute(sql, {"username":user, "password":password_hash})
    db.session.commit()

def is_user_admin(username):
    sql = "SELECT 1 FROM users WHERE name=:name AND is_admin=TRUE"
    return  db.session.execute(sql, {"name":username}).fetchone()

def create_account(user, password,):
    if does_user_exist(user):
        return False
    add_user(user, generate_password_hash(password))
    return True



