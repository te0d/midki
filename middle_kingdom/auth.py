import datetime
import functools
import re

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from middle_kingdom.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")
username_re = re.compile(r"^[\w\d]{3,32}$")

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        db = get_db()
        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif not username_re.match(username):
            error = "Username must be between 3 and 32 characters and cannot contain spaces or punctuation."
        elif len(password) < 8 or len(password) > 32:
            error = "Password must be between 8 and 32 characters."
        elif email and len(email) > 64:
            error = "Sorry, the email has too many characters."
        elif db.execute(
            "SELECT id FROM users WHERE username = ?", (username,)
        ).fetchone() is not None:
            error = "User {} already exists.".format(username)

        if error is None:
            now = datetime.datetime.now()
            db.execute(
                "INSERT INTO users (username, password, email, creation_time) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), email, now)
            )

            # populate starting words
            for hsk_level in range(1, 7):
                db.execute(
                    "INSERT INTO seen (user_id, word_id, appearance_time, question_type, answer_type) SELECT users.id, words.id, ?, 'word', 'simplified' FROM users, words WHERE users.username = ? AND words.hsk_level = ? ORDER BY overall_freq limit 5",
                    (now, username, hsk_level)
                )
                db.execute(
                    "INSERT INTO seen (user_id, word_id, appearance_time, question_type, answer_type) SELECT users.id, words.id, ?, 'word', 'traditional' FROM users, words WHERE users.username = ? AND words.hsk_level = ? ORDER BY overall_freq limit 5",
                    (now, username, hsk_level)
                )
                db.execute(
                    "INSERT INTO seen (user_id, word_id, appearance_time, question_type, answer_type) SELECT users.id, words.id, ?, 'meaning', 'simplified' FROM users, words WHERE users.username = ? AND words.hsk_level = ? ORDER BY overall_freq limit 5",
                    (now, username, hsk_level)
                )
                db.execute(
                    "INSERT INTO seen (user_id, word_id, appearance_time, question_type, answer_type) SELECT users.id, words.id, ?, 'meaning', 'traditional' FROM users, words WHERE users.username = ? AND words.hsk_level = ? ORDER BY overall_freq limit 5",
                    (now, username, hsk_level)
                )
            db.commit()
            return redirect(url_for("auth.login"))

        flash(error)

    return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        error = None
        user = db.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            error = "Incorrect login information."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("index"))

        flash(error)

    return render_template("auth/login.html")

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM users WHERE  id = ?", (user_id,)
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
