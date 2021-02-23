from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        answer = request.form["answer"]
        is_correct = "Correct!" if answer == session["word"] else "Wrong!"
        flash(is_correct)

    db = get_db()
    word = db.execute(
        "SELECT simplified FROM words ORDER BY RANDOM() LIMIT 1"
    ).fetchone()["simplified"]
    session["word"] = word
    return render_template("quiz/quiz.html", word=word)

@bp.route("/hsk<int:level>", methods=("GET", "POST"))
def hsk(level):
    if request.method == "POST":
        answer = request.form["answer"]
        is_correct = "Correct!" if answer == session["word"] else "Wrong!"
        flash(is_correct)

    db = get_db()
    word = db.execute(
        "SELECT simplified FROM words WHERE hsk_level = ? ORDER BY RANDOM() LIMIT 1",
        (level,)
    ).fetchone()["simplified"]
    session["word"] = word
    return render_template("quiz/quiz.html", word=word)
