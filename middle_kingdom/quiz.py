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

    try:
        quiz_type = "traditional" if session["quiz_type"] == "traditional" else "simplified"
    except KeyError:
        quiz_type = "simplified"


    if request.method == "POST":
        answer = request.form["answer"]
        is_correct = answer == session["word"]["quiz"]
        word_id = session["word"]["id"]
        session["word"] = None

        if g.user:
            # Record result
            db.execute(
                "INSERT INTO results (user_id, word_id, quiz_type, is_correct) VALUES (?, ?, ?, ?)",
                (g.user["id"], word_id, quiz_type, is_correct)
            )
            db.commit()

            # Expose new words
            if is_correct:
                correct_count = db.execute(
                    "SELECT COUNT(*) AS correct_count FROM results WHERE user_id = ? AND word_id = ? AND quiz_type = ? AND is_correct = 1",
                    (g.user["id"], word_id, quiz_type)
                ).fetchone()

                if correct_count["correct_count"] == 1:
                    if level:
                        db.execute(
                            "INSERT OR IGNORE INTO seen (user_id, word_id, quiz_type) SELECT ?, id, ? FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?) AND hsk_level = ?);",
                            (g.user["id"], quiz_type, g.user["id"], quiz_type, level)
                        )
                        db.commit()
                    else:
                        db.execute(
                            "INSERT OR IGNORE INTO seen (user_id, word_id, quiz_type) SELECT ?, id, ? FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?));",
                            (g.user["id"], quiz_type, g.user["id"], quiz_type)
                        )
                        db.commit()

        is_correct_text = "Correct!" if is_correct else "Wrong!"
        flash(is_correct_text, "correct" if is_correct else "wrong")

        word_info = db.execute(
            "SELECT * FROM words WHERE id = ?",
            (word_id,)
        ).fetchone()
        return render_template("quiz/answer.html", level=level, word_info=dict(word_info))

    if level:
        if g.user:
            word = db.execute(
                "SELECT id, {} as quiz FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?) AND hsk_level = ? ORDER BY RANDOM() LIMIT 1;".format(quiz_type),
                (g.user["id"], quiz_type, level)
            ).fetchone()
        else:
            word = db.execute(
                "SELECT id, {} as quiz FROM words WHERE hsk_level = ? ORDER BY RANDOM() LIMIT 1".format(quiz_type),
                (level,)
            ).fetchone()
    else:
        if g.user:
            word = db.execute(
                "SELECT id, {} as quiz FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?) ORDER BY RANDOM() LIMIT 1;".format(quiz_type),
                (g.user["id"], quiz_type)
            ).fetchone()
        else:
            word = db.execute(
                "SELECT id, {} as quiz FROM words ORDER BY RANDOM() LIMIT 1".format(quiz_type)
            ).fetchone()

    session["word"] = dict(word)
    return render_template("quiz/quiz.html", level=level, word=word)
