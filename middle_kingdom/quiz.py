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
        is_correct = answer == session["word"]["simplified"]

        if g.user:
            # Record result
            db.execute(
                "INSERT INTO results (user_id, word_id, is_correct) VALUES (?, ?, ?)",
                (g.user["id"], session["word"]["id"], is_correct)
            )
            db.commit()

            # Expose new words
            if is_correct:
                correct_count = db.execute(
                    "SELECT COUNT(*) AS correct_count FROM results WHERE user_id = ? AND word_id = ? AND is_correct = 1",
                    (g.user["id"], session["word"]["id"])
                ).fetchone()

                if correct_count["correct_count"] == 1:
                    if level:
                        db.execute(
                            "INSERT OR IGNORE INTO seen (user_id, word_id) SELECT ?, id FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ?) AND hsk_level = ?);",
                            (g.user["id"], g.user["id"], level)
                        )
                        db.commit()
                    else:
                        db.execute(
                            "INSERT OR IGNORE INTO seen (user_id, word_id) SELECT ?, id FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ?));",
                            (g.user["id"], g.user["id"])
                        )
                        db.commit()

        is_correct_text = "Correct!" if is_correct else "Wrong!"
        flash(is_correct_text)

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
    return render_template("quiz/quiz.html", level=level, word=word)
