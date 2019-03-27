""" Test cases for validating fact store persistence """
from fact_store.fact_store_api import FactStore
from fact_store.model import EventModel, FeedbackModel


def test_events_inserted():
    """
    If users do not provide a connection string. It will by default store the
    data in sqlite. We can then validate that the values we stored are correct.
    We also check that the values are 3 elements inserted will =3
    :return:
    """
    fact_store = FactStore(True)
    fact_store.session.query(EventModel).delete()
    fact_store.write_event(predict_id="a2b35c5b-016d-4e2c-8ec5-87d1b962b2f8",
                   message="kssksjs",
                   score=3.1, anomaly_status=True)
    fact_store.write_event(predict_id="18bd090d-ae27-4b19-a0db-ed5f589b4e2e",
                   message="JSJSJS",
                   score=2.2,
                   anomaly_status=False)
    fact_store.write_event(predict_id="74a6b1bd-efea-4e7b-87a9-8f7330885160",
                   message="sjsjsjsj",
                   score=8.3,
                   anomaly_status=True)
    items = fact_store.session.query(EventModel).all()
    assert len(items) is 3


def test_feedback_inserted():
    """
    This function tests that fact_store create sqlite db
    and stores as a safe default for testing feedback gets
    tracked.

    :return:
    """
    fact_store = FactStore(True)
    fact_store.session.query(FeedbackModel).delete()
    fact_store.write_feedback(
        predict_id="a2b35c5b-016d-4e2c-8ec5-87d1b962b2f8",
        notes="222JSJSJJS",
        anomaly_status=True)
    fact_store.write_feedback(
        predict_id="18bd090d-ae27-4b19-a0db-ed5f589b4e2e",
        notes="SSJJSJS",
        anomaly_status=True)
    fact_store.write_feedback(
        predict_id="74a6b1bd-efea-4e7b-87a9-8f7330885160",
        notes="AJJSJS",
        anomaly_status=False)
    items = fact_store.readall_feedback()
    assert len(items) is 3
