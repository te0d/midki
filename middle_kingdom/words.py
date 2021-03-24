from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("words", __name__)


@bp.route("/")
def index():
    db = get_db()

    if g.user:
        try:
            answer_type = "traditional" if session["answer_type"] == "traditional" else "simplified"
        except KeyError:
            answer_type = "simplified"

        hsk_levels = db.execute(
            "SELECT w.hsk_level, COUNT(distinct w.id) as total_word_count, SUM(CASE WHEN sr.question_type = 'word' THEN 1 ELSE 0 END) as correct_word_count, SUM(CASE WHEN sr.question_type = 'meaning' THEN 1 ELSE 0 END) as correct_meaning_count  FROM words w LEFT JOIN (SELECT s.id, s.word_id, s.question_type FROM seen s JOIN results r ON s.id = r.seen_id AND s.user_id = ? AND s.answer_type = ? AND r.is_correct = 1 GROUP BY s.word_id, s.question_type) sr ON w.id = sr.word_id GROUP BY w.hsk_level",
            (g.user["id"], answer_type)
        ).fetchall()
        return render_template("words/user.html", hsk_levels=[dict(row) for row in hsk_levels])
    else:
        hsk_levels = db.execute(
            "SELECT hsk_level, count(*) as total_word_count FROM words GROUP BY hsk_level ORDER BY hsk_level"
        ).fetchall()
        return render_template("words/index.html", hsk_levels=[dict(row) for row in hsk_levels])


@bp.route("/hsk<int:level>")
@bp.route("/hsk<int:level>/<question_type>")
def hsk(level, question_type=None):
    db = get_db()
    question_type = "meaning" if question_type == "meaning" else "word"

    try:
        answer_type = "traditional" if session["answer_type"] == "traditional" else "simplified"
    except KeyError:
        answer_type = "simplified"

    if g.user:
        words = db.execute(
            "SELECT sw.word_id, sw.simplified, sw.traditional, sw.pinyin_accent, sw.meaning, (CASE WHEN sw.weight <= 70 THEN 'alert-success' WHEN sw.weight >= 130 THEN 'alert-warning' ELSE '' END) AS weight_class, SUM(CASE WHEN r.is_correct = 1 THEN 1 ELSE 0 END) AS win, SUM(CASE WHEN r.is_correct = 0 THEN 1 ELSE 0 END) AS loss FROM (SELECT s.id AS seen_id, s.word_id, s.question_type, s.weight, w.simplified, w.traditional, w.pinyin_accent, w.meaning FROM seen s JOIN words w ON s.word_id = w.id WHERE s.user_id = ? AND s.question_type = ? AND s.answer_type = ? AND w.hsk_level = ?) AS sw LEFT JOIN results r ON sw.seen_id = r.seen_id GROUP BY sw.word_id;",
            (g.user["id"], question_type, answer_type, level)
        ).fetchall()
    else:
        words = db.execute(
            "SELECT simplified, traditional, pinyin_accent, meaning FROM words WHERE hsk_level = ?",
            (level,)
        ).fetchall()

    return render_template("words/hsk.html", level=level, question_type=question_type, words=words)


@bp.route("/simplified")
@bp.route("/simplified/<path:subpath>")
def simplified(subpath=None):
    session["answer_type"] = "simplified"
    if subpath:
        return redirect("/{}".format(subpath))
    else:
        return redirect(url_for("index"))


@bp.route("/traditional")
@bp.route("/traditional/<path:subpath>")
def traditional(subpath=None):
    session["answer_type"] = "traditional"
    if subpath:
        return redirect("/{}".format(subpath))
    else:
        return redirect(url_for("index"))
