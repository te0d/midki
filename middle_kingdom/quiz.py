import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/", methods=("GET", "POST"))
@bp.route("/hsk<int:level>", methods=("GET", "POST"))
def index(level=None):
    if g.user and level == None:
        # Adding new seen words is dependent on HSK level. Quizzing everything in tandem with by_level messed up new seen
        # words. Could be fixed to allow users to progress in hsk while quizzing everything.
        flash("Sorry, only HSK levels can be quizzed when logged in.")
        return redirect(url_for("words.index"))

    db = get_db()
    now = datetime.datetime.now()

    try:
        quiz_type = "traditional" if session["quiz_type"] == "traditional" else "simplified"
    except KeyError:
        quiz_type = "simplified"


    if request.method == "POST":
        answer = request.form["answer"]
        word_id = session["word"]["id"]
        question_time = session["word"]["question_time"]
        is_correct = answer == session["word"]["quiz"]
        session["word"] = None

        if g.user:
            # Record result
            db.execute(
                "INSERT INTO results (seen_id, is_correct, question_time, answer_time) SELECT id, ?, ?, ? FROM seen WHERE user_id = ? AND word_id = ? AND quiz_type = ?",
                (is_correct, question_time, now, g.user["id"], word_id, quiz_type)
            )
            db.commit()

            # Expose new words
            if is_correct:
                correct_count = db.execute(
                    "SELECT COUNT(*) AS correct_count FROM seen, results WHERE seen.id = results.seen_id AND seen.user_id = ? AND seen.word_id = ? AND seen.quiz_type = ? AND results.is_correct = 1",
                    (g.user["id"], word_id, quiz_type)
                ).fetchone()

                if correct_count["correct_count"] == 1:
                    db.execute(
                        "INSERT OR IGNORE INTO seen (user_id, word_id, appearance_time, quiz_type) SELECT ?, id, ?, ? FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?) AND hsk_level = ?);",
                        (g.user["id"], now, quiz_type, g.user["id"], quiz_type, level)
                    )
                    db.commit()

        is_correct_text = "Correct!" if is_correct else "Wrong!"
        flash(is_correct_text, "correct" if is_correct else "wrong")

        word_info = db.execute(
            "SELECT * FROM words WHERE id = ?",
            (word_id,)
        ).fetchone()
        return render_template("quiz/answer.html", level=level, word_info=dict(word_info))

    if g.user:
        word = db.execute(
            "SELECT id, {} as quiz FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ? AND quiz_type = ?) AND hsk_level = ? ORDER BY RANDOM() LIMIT 1;".format(quiz_type),
            (g.user["id"], quiz_type, level)
        ).fetchone()
    elif level:
        word = db.execute(
            "SELECT id, {} as quiz FROM words WHERE hsk_level = ? ORDER BY RANDOM() LIMIT 1".format(quiz_type),
            (level,)
        ).fetchone()
    else:
        word = db.execute(
            "SELECT id, {} as quiz FROM words ORDER BY RANDOM() LIMIT 1".format(quiz_type)
        ).fetchone()

    session["word"] = dict(word)
    session["word"]["question_time"] = now

    return render_template("quiz/quiz.html", level=level, word=word)
