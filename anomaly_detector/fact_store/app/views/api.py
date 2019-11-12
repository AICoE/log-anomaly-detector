"""Factstore Api definition."""
import logging
import os
from flask import request, jsonify, make_response
from flask import Blueprint
from prometheus_client import Counter

from anomaly_detector.fact_store.app.models.controller import readall_feedback, \
    readall_false_positive, write_feedback

api = Blueprint('api', __name__, url_prefix='/api')

HUMAN_FEEDBACK_COUNT = Counter(
    "aiops_human_feedback",
    "count of number of human feedback provided by customer",
    ['customer_id', 'anomaly_status']
)
HUMAN_FEEDBACK_ERROR_COUNT = Counter(
    "aiops_human_feedback_error",
    "count of human feedback not able to write to db",
    ['err_msg']
)


@api.route("/metadata", methods=["GET"])
def metadata():
    """
    Metadata Service.

    Provide list of false anomalies to be relabeled during ml training run.
    """
    df = readall_feedback()
    return jsonify({"feedback": df})


@api.route("/false_positive", methods=["GET"])
def false_positive():
    """
    False Positive Service.

    Provide list of false anomalies to be relabeled during ml training run.
    """
    df = readall_false_positive()
    return jsonify({"feedback": df})


@api.route("/feedback", methods=["POST"])
def feedback():
    """
    Feedback Service.

    Provide user input on which false predictions this model provided.
    """
    content = request.json
    # When deploying fact_store per customer you should set env var
    customer_id = os.getenv("CUSTOMER_ID")
    try:
        logging.info("id: {} ".format(content["lad_id"]))
        logging.info("anomaly: {} ".format(content["is_anomaly"]))
        logging.info("message: {} ".format(content["message"]))
        logging.info("customer_id: {} ".format(customer_id))
    except KeyError as e:
        msg = "Encountered key error: {}".format(e)
        logging.error(msg)
        return make_response(msg, 500)

    if not content["lad_id"] or content["is_anomaly"] == "":
        msg = "This service requires that you provide the id and " \
              "anomaly=True|False. Messages are optional."
        logging.error(msg)
        return make_response(msg, 500)

    # Record feedback
    HUMAN_FEEDBACK_COUNT.labels(
        customer_id=customer_id,
        anomaly_status=content["is_anomaly"]
    ).inc()

    try:
        # Note id is the prediction id that is found in the email.
        write_feedback(
            predict_id=content["lad_id"], message=content["message"],
            anomaly_status=content["is_anomaly"].lower() == 'true',
            customer_id=customer_id
        )
    except Exception as e:
        logging.info(e)
        HUMAN_FEEDBACK_ERROR_COUNT.labels(
            err_msg="failure to write to db in factstore"
        ).inc()
        result = {"feedback_service": "failure", "error_msg": "{0}".format(e)}
        return make_response(jsonify(result), 403)
    else:
        result = {"feedback_service": "success"}
        return make_response(jsonify(result), 200)
