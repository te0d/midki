from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
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
    words = db.execute(
        "SELECT simplified FROM words WHERE hsk_level = ?",
        (level,)
    ).fetchall()
    return render_template("words/hsk.html", level=level, words=[w["simplified"] for w in words])
