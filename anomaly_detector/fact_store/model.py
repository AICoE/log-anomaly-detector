"""Model orm table descriptor."""
from sqlalchemy import Column, Integer, String, Float, Boolean, Sequence, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FeedbackModel(Base):
    """FeedbackModel persists user feedback."""

    __tablename__ = "feedback"
    id = Column(Integer, Sequence("id_seq"), primary_key=True, autoincrement=True)
    # Required
    predict_id = Column(String(255), nullable=False)
    # Required
    message = Column(String(2000), nullable=False)
    # Required
    reported_anomaly_status = Column(Boolean, nullable=False)

    def __repr__(self):
        """Repr - Used for debugging to see repr output."""
        return "<Feedback %r>" % self.notes

    def to_dict(self):
        """Convert results into dictionary for json response."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
