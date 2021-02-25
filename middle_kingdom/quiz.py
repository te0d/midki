from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/", methods=("GET", "POST"))
@bp.route("/hsk<int:level>", methods=("GET", "POST"))
def index(level=None):
    db = get_db()
    if request.method == "POST":
        answer = request.form["answer"]
        is_correct = "Correct!" if answer == session["word"]["simplified"] else "Wrong!"
        flash(is_correct)
        word_info = db.execute(
            "SELECT * FROM words WHERE id = ?",
            (session["word"]["id"],)
        ).fetchone()
        return render_template("quiz/answer.html", level=level, word_info=dict(word_info))

    if level:
        if g.user:
            word = db.execute(
                "SELECT id, simplified FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ?) AND hsk_level = ? ORDER BY RANDOM() LIMIT 1;",
                (g.user["id"], level)
            ).fetchone()
        else:
            word = db.execute(
                "SELECT id, simplified FROM words WHERE hsk_level = ? ORDER BY RANDOM() LIMIT 1",
                (level,)
            ).fetchone()
    else:
        if g.user:
            word = db.execute(
                "SELECT id, simplified FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ?) ORDER BY RANDOM() LIMIT 1;",
                (g.user["id"],)
            ).fetchone()
        else:
            word = db.execute(
                "SELECT id, simplified FROM words ORDER BY RANDOM() LIMIT 1"
            ).fetchone()

    session["word"] = dict(word)
    return render_template("quiz/quiz.html", word=word)
