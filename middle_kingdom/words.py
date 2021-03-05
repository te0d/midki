from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.exceptions import abort

from middle_kingdom.db import get_db

bp = Blueprint("words", __name__)


@bp.route("/")
def index():
    db = get_db()
    hsk_levels = db.execute(
        "SELECT DISTINCT hsk_level FROM words ORDER BY hsk_level"
    ).fetchall()
    return render_template("words/index.html", hsk_levels=[l["hsk_level"] for l in hsk_levels])

@bp.route("/hsk<int:level>")
def hsk(level):
    db = get_db()

    try:
        quiz_type = "traditional" if session["quiz_type"] == "traditional" else "simplified"
    except KeyError:
        quiz_type = "simplified"

    if g.user:
        words = db.execute(
            "SELECT seenwords.word_id, seenwords.simplified, seenwords.traditional, seenwords.pinyin_accent, seenwords.meaning, SUM(CASE WHEN results.is_correct = 1 THEN 1 ELSE 0 END) as win, SUM(CASE WHEN results.is_correct = 0 THEN 1 ELSE 0 END) as loss FROM (SELECT seen.word_id, words.simplified, words.traditional, words.pinyin_accent, words.meaning FROM seen JOIN words ON seen.word_id = words.id WHERE seen.user_id = ? AND seen.quiz_type = ? AND words.hsk_level = ?) as seenwords LEFT JOIN results ON seenwords.word_id = results.word_id AND results.quiz_type = ? GROUP BY seenwords.word_id;",
            (g.user["id"], quiz_type, level, quiz_type)
        ).fetchall()
    else:
        words = db.execute(
            "SELECT simplified, traditional, pinyin_accent, meaning FROM words WHERE hsk_level = ?",
            (level,)
        ).fetchall()

    return render_template("words/hsk.html", level=level, words=words)

@bp.route("/simplified")
def simplified():
    session["quiz_type"] = "simplified"
    return redirect(url_for("index"))

@bp.route("/traditional")
def traditional():
    session["quiz_type"] = "traditional"
    return redirect(url_for("index"))
