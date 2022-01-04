from app import app
from db import db
from flask import redirect, render_template, request, session, abort, make_response
from flask_sqlalchemy import SQLAlchemy
from post_dao import PostDAO

import user
import session
import thread_db

def display_error(desc, msg):
    return render_template("error.html", error_name=desc, error_msg=msg)

def verify_csrf():
    if not session.check_csrf_token(request.form["csrf_token"]):
        abort(403)

def verify_user_is_admin():
    if not user.is_user_admin(session.get_session_user()):
        abort(403)

@app.route("/")
def index():
    username = session.get_session_user()
    topics = db.session.execute("SELECT * FROM topics WHERE is_deleted=FALSE").fetchall()
    return render_template("index.html", user=username, topics=topics, is_admin=user.is_user_admin(username))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        if user.create_account(request.form["username"], request.form["password"], request.form["password2"]):
            session.login_as(request.form["username"])
            return redirect("/")
        return display_error("Rekisteröityminen epäonnistui", "")
    
    elif request.method == "GET":
        return render_template("register.html")


@app.route("/login", methods=["POST"])
def login_redirect():
    username = request.form["username"]
    passw = request.form["password"]
    if user.check_user_credentials(username, passw):
        session.login_as(username)
        return redirect("/")
    return redirect("/login_fail")


@app.route("/logout")
def logout():
    session.end_session()
    return redirect("/")

@app.route("/login_fail")
def login_failed():
    return display_error("Kirjautuminen epäonnistui", "Väärä käyttäjänimi tai salasana")


@app.route("/topics/<int:topic_id>")
def view_topic(topic_id):
    threads = thread_db.get_thread_list(topic_id)
    username = session.get_user_id() #name would be better
    topic = PostDAO(db).get_topic_by_id(topic_id)
    if topic == None:
        return display_error("Virheellinen keskustelualue!","")
    return render_template("topic.html", threads=threads, topic_id=topic_id, username = username, topic_name = topic.name)


@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    dao = PostDAO(db)
    posts = dao.get_posts_by_thread(thread_id)
    if len(posts) == 0:
        return display_error("Virheellinen keskusteluketju!", "")
    thread_name = thread_db.get_thread_name(thread_id)
    topic = thread_db.get_thread_topic(thread_id)
    logged_in = session.get_session_user() != None
    return render_template("thread.html",  posts=posts, thread_name=thread_name, thread_id=thread_id,
            topic=topic, logged_in=logged_in)

@app.route("/create_post/<int:thread_id>", methods=["POST"])
def post_in_thread(thread_id):
    verify_csrf()
    dao = PostDAO(db)
    user_id = session.get_user_id()
    message = request.form["message"]
    file = request.files["post_file"]
    filedata = file.read()
    if len(filedata) > 1024*1024:
        return display_error("Tiedosto on liian suuri", "Tiedosto saa olla enintään 1MB kokoinen")
    print("tiedoston nimi:",file.name)

    if user_id != None and len(message) > 0:
        if len(filedata) > 0:
            dao.create_post_with_file(thread_id, message, user_id, file.filename, filedata)
        else:
            dao.create_post(thread_id, message, user_id)
    return redirect("/thread/" + str(thread_id))

@app.route("/create_thread/<int:topic_id>", methods=["POST"])
def create_new_thread(topic_id):
    verify_csrf()

    thread_name = request.form["thread_name"]
    message = request.form["message"]
    user_id = session.get_user_id()
    if len(message) == 0:
        return display_error("Viestiketjun luonti epäonnistui", "Aloitusviesti ei saa olla tyhjä")

    if len(thread_name) == 0:
        return display_error("Viestiketjun luonti epäonnistui", "Viestiketjun nimi ei saa olla tyhjä")
    
    if user_id == None:
        return display_error("Vain rekisteröityneet käyttäjät voivat tehdä viestiketjuja", "")

    thread_id = thread_db.create_thread_with_post(thread_name, message, user_id, topic_id)
    return redirect("/thread/" + str(thread_id))


@app.route("/delete_topic/<int:id>", methods=["POST"])
def delete_topic(id):
    verify_csrf()
    verify_user_is_admin()
    PostDAO(db).delete_topic(id)
    return redirect("/")

@app.route("/create_topic", methods=["POST"])
def create_topic():
    verify_csrf()
    verify_user_is_admin()
    topic_name = request.form["name"]
    topic_description = request.form["desc"]
    PostDAO(db).create_topic(topic_name, topic_description)
    return redirect("/")

@app.route("/file/<int:id>/<string:filename>")
def view_file(id, filename):
    file = PostDAO(db).get_file(id)
    if file == None:
        return display_error("Virheellinen tiedosto", "hakemaasi tiedostoa ei ole olemassa")
    response = make_response(file.data)
    response.headers.set("Content-Type", file.get_mimetype())
    return response

