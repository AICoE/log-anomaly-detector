"""Fact Store API for human feedback in the loop."""
import logging

from sqlalchemy.exc import IntegrityError

from anomaly_detector.fact_store.app.models.model import FeedbackModel
from anomaly_detector.fact_store.app.models.model import db as database
from contextlib import contextmanager


@contextmanager
def db_scope():
    """Provide a transactional scope around a series of operations."""
    try:
        yield database
    except Exception as e:
        database.session.rollback()
        raise e
    finally:
        database.session.close()


def write_feedback(predict_id, message, anomaly_status, customer_id):
    """Service for storage of metadata in parquet.

    :param message: feed back message
    :param customer_id: customer identifier
    :param predict_id: predict Id where the anomaly details are stored
    :param anomaly_status: is this anomaly correctly reported or false.
    """
    # Add id to bloom filter so we don't have to hit the database everytime
    feedback = FeedbackModel(
        predict_id=predict_id,
        message=message,
        reported_anomaly_status=anomaly_status,
        customer_id=customer_id
    )

    with db_scope() as db:
        try:
            db.session.add(feedback)
            db.session.commit()
            logging.info(
                "Persisted ID: {} recorded in FStore".format(feedback.id)
            )
        except IntegrityError as e:
            logging.error("Encountered integrity error while writing to db: "
                          "{}".format(e))
            raise e
        except Exception as e:
            logging.error("Could not write feedback.")
            raise e


def readall_feedback():
    """Service for querying datastore of current false anomalies."""
    with db_scope() as db:
        try:
            feedbacks = db.session.query(FeedbackModel).all()
        except Exception as e:
            logging.error("Could not read feedback.")
            raise e
    feedback_data = [f.to_dict() for f in feedbacks]
    return feedback_data


def readall_false_positive():
    """Service for querying datastore of current false anomalies."""
    with db_scope() as db:
        try:
            items = db.session.query(FeedbackModel).all()
        except Exception as e:
            logging.error("Could not read false positive data.")
            raise e
    messages = set()
    for i in items:
        if i.reported_anomaly_status is True:
            messages.add(i.message)

    return list(messages)
