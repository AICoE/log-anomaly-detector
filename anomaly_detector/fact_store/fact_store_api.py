"""Fact Store API for human feedback in the loop."""
import os
from anomaly_detector.fact_store.model import EventModel, FeedbackModel, Base
from pybloom import BloomFilter
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class FactStore(object):
    """FactStore: Service for feedback collection on accuracy of machine learning."""

    f = BloomFilter(capacity=1000, error_rate=0.001)

    def __init__(self, autocreate=True):
        """We initialize our sqlalchemy connection and setup the database."""
        engine = create_engine(os.getenv("SQL_CONNECT", "sqlite:////tmp/test.db"), echo=True)
        try:
            if autocreate is True:
                print("Creating tables")
                Base.metadata.create_all(engine)
        except Exception as e:
            print("Exception occurred: {} ".format(e))
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def write_event(self, predict_id, message, score, anomaly_status):
        """Service for storage of event metadata in parquet.

        :param id: predict Id where the anomaly details are stored
        :param message: the original message that triggered the anomaly
        :param score: the score that the algorithm set this anomaly
        :param anomaly_status: is this anomaly correct or false
        :return: None
        """
        event = EventModel(message=message, score=score, predict_id=predict_id, anomaly_status=anomaly_status)
        self.session.add(event)
        self.session.commit()
        print("Event ID: {}  recorded in events_store".format(event.predict_id))

    def write_feedback(self, predict_id, notes, anomaly_status):
        """Service for storage of metadata in parquet.

        :param predict_id: predict Id where the anomaly details are stored
        :param notes: notes to provide more detail on why this is false
               flagged anomaly
        :param anomaly_status: is this anomaly correctly reported or false.
        :return:
        """
        # Adding id to bloom filter so we don't have to hit the database every time
        if self.f.add(predict_id) is False:
            feedback = FeedbackModel(predict_id=predict_id, notes=notes, reported_anomaly_status=anomaly_status)
            self.session.add(feedback)
            self.session.commit()
            print("Persisted ID: {} recorded in FStore".format(feedback.id))
            return True
        else:
            return False
        return True

    def readall_feedback(self):
        """Service for querying datastore of current false anomalies."""
        feedbacks = self.session.query(FeedbackModel).all()
        list = [f.to_dict() for f in feedbacks]
        return list

    def is_not_anomaly(self, _id):
        """Check if anomaly id is in the bloom filter."""
        return _id in self.f
