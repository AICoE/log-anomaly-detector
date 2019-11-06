"""Test cases for validating fact store persistence."""
from anomaly_detector.fact_store.api import FactStore
from anomaly_detector.fact_store.model import FeedbackModel
import pytest


@pytest.mark.factstore
def test_feedback_inserted(sample_feedback):
    """Test inserting events into the fact_store."""
    fact_store = FactStore(True)
    fact_store.session.query(FeedbackModel).delete()
    for feedback in sample_feedback:
        fact_store.write_feedback(**feedback)
    items = fact_store.readall_feedback()
    assert len(items) is 3
