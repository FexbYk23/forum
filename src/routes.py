from app import app
from db import db
from flask import redirect, render_template, request, session, abort, make_response
from flask_sqlalchemy import SQLAlchemy


import user
import session
import thread_db
import post_db
import input_validation

def display_error(desc, msg):
    return render_template("error.html", error_name=desc, error_msg=msg)

def verify_csrf():
    if not session.check_csrf_token(request.form["csrf_token"]):
        abort(403)

def verify_user_is_admin():
    if not user.is_user_admin(session.get_session_user()):
        abort(403)

def return_redirect():
        return redirect(request.form.get("redirect", "/"))


@app.route("/")
def index():
    username = session.get_session_user()
    topics = db.session.execute("SELECT * FROM topics WHERE is_deleted=FALSE").fetchall()
    return render_template("index.html", user=username, topics=topics, is_admin=user.is_user_admin(username))


@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        pass1 = request.form["password"]
        pass2 = request.form["password2"]
        
        valid = input_validation.is_registration_valid(username, pass1, pass2)
        if not valid[0]:
            return display_error("Rekisteröityminen epäonnistui",valid[1])

        if user.create_account(username, pass1):
            session.login_as(request.form["username"])
            return redirect("/")
        return display_error("Rekisteröityminen epäonnistui", "nimi on jo käytössä")
    
    elif request.method == "GET":
        return render_template("register.html")


@app.route("/login", methods=["POST"])
def return_redirect_page():
    username = request.form["username"]
    passw = request.form["password"]
    if user.check_user_credentials(username, passw):
        session.login_as(username)
        return return_redirect()
    return display_error("Kirjautuminen epäonnistui",
            "Väärä käyttäjänimi tai salasana")


@app.route("/logout")
def logout():
    session.end_session()
    return return_redirect()

@app.route("/topics/<int:topic_id>")
def view_topic(topic_id):
    threads = thread_db.get_thread_list(topic_id)
    username = session.get_session_user()
    topic = post_db.get_topic_by_id(topic_id)
    is_admin = user.is_user_admin(session.get_session_user())
    if topic == None:
        return display_error("Virheellinen keskustelualue!","")
    return render_template("topic.html", threads=threads, topic_id=topic_id,
            user = username, topic_name = topic.name, is_admin=is_admin)


@app.route("/thread/<int:thread_id>")
def view_thread(thread_id):
    posts = post_db.get_posts_by_thread(thread_id)
    if len(posts) == 0 or thread_db.get_thread(thread_id).is_deleted:
        return display_error("Virheellinen keskusteluketju!", "")
    
    username = session.get_session_user()
    is_admin = user.is_user_admin(username)

    for post in posts:
        if post.poster == username or is_admin:
            post.can_delete = True
    thread_name = thread_db.get_thread_name(thread_id)
    topic = thread_db.get_thread_topic(thread_id)
    logged_in = session.get_session_user() != None
    return render_template("thread.html",  posts=posts, thread_name=thread_name, thread_id=thread_id,
            topic=topic, logged_in=logged_in, user=username)


@app.route("/create_post/<int:thread_id>", methods=["POST"])
def post_in_thread(thread_id):
    verify_csrf()
    user_id = session.get_user_id()
    message = request.form["message"]
    file = request.files["post_file"]
    filedata = file.read()
    if len(filedata) > 1024*1024:
        return display_error("Tiedosto on liian suuri", "Tiedosto saa olla enintään 1MB kokoinen")
    
    valid = input_validation.is_post_valid(user_id, message)
    if not valid[0]:
        return display_error(valid[1], "")

    if len(filedata) > 0:
        post_db.create_post_with_file(thread_id, message, user_id, file.filename, filedata)
    else:
        post_db.create_post(thread_id, message, user_id, None)


    return redirect("/thread/" + str(thread_id))

@app.route("/create_thread/<int:topic_id>", methods=["POST"])
def create_new_thread(topic_id):
    verify_csrf()

    thread_name = request.form["thread_name"]
    message = request.form["message"]
    user_id = session.get_user_id()
    file = request.files["post_file"]
    
    post_valid = input_validation.is_post_valid(user_id, message)
    if not post_valid[0]:
        return display_error(post_valid[1],"")

    thread_valid = input_validation.is_thread_name_valid(thread_name)
    if not thread_valid[0]:
        return display_error(thread_valid[1],"")
    
    filedata = file.read()
    if len(filedata) > 1024*1024:
        return display_error("Tiedosto on liian suuri", "Tiedosto saa olla enintään 1MB kokoinen")
    
    thread_id = thread_db.create_thread(topic_id, thread_name)

    if len(filedata) > 0:
        post_db.create_post_with_file(thread_id, message, user_id, file.filename, filedata)
    else:
        post_db.create_post(thread_id, message, user_id, None)

    return redirect("/thread/" + str(thread_id))


@app.route("/delete_topic/<int:id>", methods=["POST"])
def delete_topic(id):
    verify_csrf()
    verify_user_is_admin()
    post_db.delete_topic(id)
    return redirect("/")

@app.route("/create_topic", methods=["POST"])
def create_topic():
    verify_csrf()
    verify_user_is_admin()
    topic_name = request.form["name"]
    topic_description = request.form["desc"]
    post_db.create_topic(topic_name, topic_description)
    return redirect("/")

@app.route("/file/<int:id>/<string:filename>")
def view_file(id, filename):
    file = post_db.get_file(id)
    if file == None or post_db.is_file_thread_deleted(id):
        return display_error("Virheellinen tiedosto", "hakemaasi tiedostoa ei ole olemassa")
    response = make_response(file.data)
    response.headers.set("Content-Type", file.get_mimetype())
    return response


@app.route("/delete_post/<int:id>", methods=["POST"])
def delete_post(id):
    verify_csrf()
    username = session.get_session_user()
    is_admin = user.is_user_admin(username)
    post = post_db.get_post(id)
    if post.poster == username or is_admin:
        post_db.delete_post(id)
        return redirect("/thread/" + str(post.thread))
    else:
        abort(403)

@app.route("/delete_thread/<int:id>", methods=["POST"])
def delete_thread(id):
    verify_csrf()
    verify_user_is_admin()
    thread_db.delete_thread(id)
    return return_redirect()
