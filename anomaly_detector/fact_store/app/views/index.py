"""Factstore Index route."""
from flask import request
from flask import Blueprint, render_template
index_blueprint = Blueprint('index', __name__, template_folder='templates')


@index_blueprint.route("/")
def index():
    """Render main html page for fact_store."""
    _id = request.args.get("lad_id")
    _msg = request.args.get("message")
    _is_anomaly = request.args.get("is_anomaly")
    if _id is None:
        return render_template("index.html")
    return render_template(
        "index.html",
        id=_id,
        msg=_msg,
        is_anomaly=_is_anomaly
    )
