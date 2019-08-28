"""Fact Store API for human feedback in the loop."""
import os
from anomaly_detector.fact_store.model import FeedbackModel, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import json
import logging


class FactStore(object):
    """FactStore: Service for feedback collection on accuracy of machine learning."""

    def __init__(self, autocreate=True):
        """We initialize our sqlalchemy connection and setup the database."""
        engine = create_engine(os.getenv("SQL_CONNECT", "sqlite://"), echo=True)
        try:
            if autocreate is True:
                logging.info("Creating tables")
                Base.metadata.create_all(engine)
        except Exception as e:
            logging.error("Exception occurred: {} ".format(e))
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def write_feedback(self, predict_id, message, anomaly_status):
        """Service for storage of metadata in parquet.

        :param predict_id: predict Id where the anomaly details are stored
        :param notes: notes to provide more detail on why this is false
               flagged anomaly
        :param anomaly_status: is this anomaly correctly reported or false.
        :return:
        """
        # Adding id to bloom filter so we don't have to hit the database every time

        feedback = FeedbackModel(predict_id=predict_id, message=message, reported_anomaly_status=anomaly_status)
        self.session.add(feedback)
        self.session.commit()
        logging.info("Persisted ID: {} recorded in FStore".format(feedback.id))
        return True

    def readall_feedback(self):
        """Service for querying datastore of current false anomalies."""
        feedbacks = self.session.query(FeedbackModel).all()
        list = [f.to_dict() for f in feedbacks]
        return list

    def readall_false_positive(self):
        """Service for querying datastore of current false anomalies."""
        items = self.session.query(FeedbackModel).all()
        messages = set()
        for i in items:
            if i.reported_anomaly_status is True:
                messages.add(i.message)

        return list(messages)
