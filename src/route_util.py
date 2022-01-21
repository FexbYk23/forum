from flask import redirect, render_template, request, session, abort, make_response
import db.user as user
import session


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



