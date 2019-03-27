from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float,\
    Boolean, Sequence, ForeignKey
"""Model.py
Sqlalchemy is used to generate tables and allow for creating,
updating, deleting and read operations on sql database. If
you change the model definition you will need to drop the
tables and regenerate your schema.
"""
Base = declarative_base()


class EventModel(Base):
    """
    Model Used for persisting events when model generates a prediction.
    We track this for quality control
    """
    __tablename__ = "events"
    predict_id = Column(String(255),
                        nullable=False,
                        primary_key=True,
                        unique=True)
    message = Column(String(255),
                     nullable=False)
    score = Column(Float,
                   nullable=False)
    anomaly_status = Column(Boolean,
                            nullable=False)
    children = relationship("FeedbackModel")

    def __repr__(self):
        return '<Event %r>' % self.message

    def to_dict(self):
        """ Converts rows returned into dictionary to which is serializable
        to json
        """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class FeedbackModel(Base):
    """FeedbackModel

    Persists user feedback to track false predictions that they found.
    We will use this data for filtering notifications on anomalies

    """
    __tablename__ = "feedback"
    id = Column(Integer,
                Sequence('id_seq'),
                primary_key=True,
                autoincrement=True)
    # Required
    predict_id = Column(String(255),
                        ForeignKey('events.predict_id'),
                        nullable=False)
    # Required
    notes = Column(String(255),
                   nullable=False)
    # Required
    reported_anomaly_status = Column(Boolean,
                                     nullable=False)

    def __repr__(self):
        return '<Feedback %r>' % self.notes

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
