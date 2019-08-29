"""Fact Store main rest interface."""
import logging
from flask import Flask, request, render_template, jsonify, make_response
from anomaly_detector.fact_store.fact_store_api import FactStore

app = Flask(__name__, static_folder="static")


@app.route("/")
def index():
    """Render main html page for fact_store."""
    _id = request.args.get("lad_id")
    _msg = request.args.get("message")
    _is_anomaly = request.args.get("is_anomaly")
    if _id is None:
        return render_template("index.html")
    return render_template("index.html", id=_id, msg=_msg, is_anomaly=_is_anomaly)


@app.route("/api/metadata", methods=["GET"])
def metadata():
    """Service to provide list of false anomalies to be relabeled during ml training run."""
    fs = FactStore()
    df = fs.readall_feedback()
    return jsonify({"feedback": df})


@app.route("/api/false_positive", methods=["GET"])
def false_positive():
    """Service to provide list of false anomalies to be relabeled during ml training run."""
    fs = FactStore()
    df = fs.readall_false_positive()
    return jsonify({"feedback": df})


@app.route("/api/feedback", methods=["POST"])
def feedback():
    """Feedback Service to provide user input on which false predictions this model provided."""
    try:
        content = request.json
        logging.info("id: {} ".format(content["lad_id"]))
        logging.info("anomaly: {} ".format(content["is_anomaly"]))
        logging.info("message: {} ".format(content["message"]))

        if not content["lad_id"] or not content["is_anomaly"]:
            raise Exception(
                "This service requires that you provide the id" +
                ", anomaly=True|False and notes are optional "
            )

        fs = FactStore()

        # Note id is the prediction id that is found in the email.
        if (
                fs.write_feedback(
                    predict_id=content["lad_id"], message=content["message"], anomaly_status=bool(content["is_anomaly"])
                )
                is False
        ):
            raise Exception("Predict ID must be unique. This anomaly" + " feedback  has been reported before")
    except Exception as e:
        logging.info(e)
        result = {"feedback_service": "failure", "error_msg": "{0}".format(e)}
        return make_response(jsonify(result), 403)
    else:
        result = {"feedback_service": "success"}
        return make_response(jsonify(result), 200)

    return ""


@app.route("/api/anomaly_event", methods=["POST"])
def false_anomaly():
    """Tag false anomalies in database."""
    content = request.get_json()
    fs = FactStore()
    id = content["predict_id"]
    # Tracking event in fact-store
    res = fs.write_event(content["predict_id"], content["message"], content["score"], content["anomaly_status"])
    # Returning status if this anomaly is real anomaly_status== false
    return jsonify({"false_anomaly": res})


if __name__ == "__main__":
    app.run(debug=True, port=8080, host="0.0.0.0")
