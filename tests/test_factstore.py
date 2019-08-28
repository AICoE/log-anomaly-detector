"""Test cases for validating fact store persistence."""
from anomaly_detector.fact_store.fact_store_api import FactStore
from anomaly_detector.fact_store.model import FeedbackModel


def test_feedback_inserted():
    """Test inserting events into the fact_store."""
    fact_store = FactStore(True)
    fact_store.session.query(FeedbackModel).delete()
    fact_store.write_feedback(
        predict_id="a2b35c5b-016d-4e2c-8ec5-87d1b962b2f8", message="222JSJSJJS", anomaly_status=True
    )
    fact_store.write_feedback(predict_id="18bd090d-ae27-4b19-a0db-ed5f589b4e2e", message="SSJJSJS", anomaly_status=True)
    fact_store.write_feedback(predict_id="74a6b1bd-efea-4e7b-87a9-8f7330885160", message="AJJSJS", anomaly_status=False)
    items = fact_store.readall_feedback()
    assert len(items) is 3
