"""Model orm table descriptor."""
import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class FeedbackModel(db.Model):
    """FeedbackModel persists user feedback."""

    __tablename__ = "feedback"
    id = db.Column(db.Integer, db.Sequence("id_seq"),
                   primary_key=True, autoincrement=True)
    # Required
    predict_id = db.Column(db.String(255), unique=True, nullable=False)
    # Required
    message = db.Column(db.String(2000), nullable=False)
    # Required
    reported_anomaly_status = db.Column(db.Boolean, nullable=False)
    # Default track last date of
    created_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    # CustomerID
    customer_id = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        """Repr - Used for debugging to see repr output."""
        return "<Feedback %r>" % self.notes

    def to_dict(self):
        """Convert results into dictionary for json response."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
