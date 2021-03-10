import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


@bp.route("/<string:question_type>", methods=("GET", "POST"))
@bp.route("/<string:question_type>/hsk<int:level>", methods=("GET", "POST"))
def index(question_type, level=None):
    if question_type not in ["word", "meaning"]:
        flash("Sorry, only words or their meaning can be quizzed.")
        return redirect(url_for("words.index"))

    if g.user and level == None:
        # Adding new seen words is dependent on HSK level. Quizzing everything in tandem with by_level messed up new seen
        # words. Could be fixed to allow users to progress in hsk while quizzing everything.
        flash("Sorry, only HSK levels can be quizzed when logged in.")
        return redirect(url_for("words.index"))

    db = get_db()
    now = datetime.datetime.now()

    try:
        answer_type = "traditional" if session["answer_type"] == "traditional" else "simplified"
    except KeyError:
        answer_type = "simplified"


    if request.method == "POST":
        answer = request.form["answer"]
        word_id = session["word"]["id"]
        question_time = session["word"]["question_time"]
        is_correct = answer == session["word"]["answer"]
        session["word"] = None

        if g.user:
            # Record result
            db.execute(
                "INSERT INTO results (seen_id, is_correct, question_time, answer_time) SELECT id, ?, ?, ? FROM seen WHERE user_id = ? AND word_id = ? AND question_type = ? AND answer_type = ?",
                (is_correct, question_time, now, g.user["id"], word_id, question_type, answer_type)
            )
            db.commit()

            # Expose new words
            if is_correct:
                correct_count = db.execute(
                    "SELECT COUNT(*) AS correct_count FROM seen, results WHERE seen.id = results.seen_id AND seen.user_id = ? AND seen.word_id = ? AND seen.question_type = ? AND seen.answer_type = ? AND results.is_correct = 1",
                    (g.user["id"], word_id, question_type, answer_type)
                ).fetchone()

                if correct_count["correct_count"] == 1:
                    db.execute(
                        "INSERT OR IGNORE INTO seen (user_id, word_id, appearance_time, question_type, answer_type) SELECT ?, id, ?, ?, ? FROM (SELECT id, MIN(overall_freq) FROM words WHERE id NOT IN (SELECT word_id FROM seen WHERE user_id = ? AND question_type = ? AND answer_type = ?) AND hsk_level = ?);",
                        (g.user["id"], now, question_type, answer_type, g.user["id"], question_type, answer_type, level)
                    )
                    db.commit()

        is_correct_text = "Correct!" if is_correct else "Wrong!"
        flash(is_correct_text, "correct" if is_correct else "wrong")

        word_info = db.execute(
            "SELECT * FROM words WHERE id = ?",
            (word_id,)
        ).fetchone()
        return render_template("quiz/answer.html", level=level, word_info=dict(word_info), question_type=question_type)

    question_col = "meaning" if question_type == "meaning" else answer_type
    if g.user:
        word = db.execute(
            "SELECT id, {} as quiz, {} as answer FROM words WHERE id IN (SELECT word_id FROM seen WHERE user_id = ? AND question_type = ? AND answer_type = ?) AND hsk_level = ? ORDER BY RANDOM() LIMIT 1;".format(question_col, answer_type),
            (g.user["id"], question_type, answer_type, level)
        ).fetchone()
    elif level:
        word = db.execute(
            "SELECT id, {} as quiz, {} as answer FROM words WHERE hsk_level = ? ORDER BY RANDOM() LIMIT 1".format(question_col, answer_type),
            (level,)
        ).fetchone()
    else:
        word = db.execute(
            "SELECT id, {} as quiz, {} as answer FROM words ORDER BY RANDOM() LIMIT 1".format(question_col, answer_type)
        ).fetchone()

    session["word"] = dict(word)
    session["word"]["question_time"] = now

    return render_template("quiz/quiz.html", level=level, word=word, question_type=question_type)
