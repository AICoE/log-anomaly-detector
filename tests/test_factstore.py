"""Test cases for validating fact store persistence."""
import uuid
from anomaly_detector.fact_store.app.models.controller import write_feedback
from anomaly_detector.fact_store.app.models.controller import readall_feedback
from anomaly_detector.fact_store.app.models.model import FeedbackModel
from tests.conftest import generate_feedback


def test_home_page(test_client):
    """Test index route."""
    response = test_client.get('/')
    assert response.status_code == 200


def test_feedback_inserted(test_client, database, sample_feedback):
    """Test feedback insertions to db."""
    # Even though test_client isn't used directly, we require it to
    # create the flask application context

    database.session.query(FeedbackModel).delete()
    for feedback in sample_feedback:
        write_feedback(**feedback)
    items = readall_feedback()
    assert len(items) is 3


def test_api_feedback(test_client, monkeypatch):
    """Test feedback insertion via api."""
    items_in_db = len(readall_feedback())
    monkeypatch.setenv("CUSTOMER_ID", "1234")
    response = test_client.post('/api/feedback',
                                json=generate_feedback())
    assert response.status_code == 200

    expected_items_in_db = items_in_db + 1
    items = readall_feedback()
    assert len(items) is expected_items_in_db


def test_api_false_positive(test_client, monkeypatch):
    """Test false anomaly insertions and retrievals."""
    def count_feedback(r): return len(r.json['feedback'])

    # Add in a feedback indicating an anomaly
    monkeypatch.setenv("CUSTOMER_ID", str(uuid.uuid4()))
    response = test_client.post('/api/feedback', json=generate_feedback("True"))
    assert response.status_code == 200

    # Record the number of feed back indicating an anomaly
    response = test_client.get('/api/false_positive')
    assert response.status_code == 200
    number_of_anomalies = count_feedback(response)

    # Add in a non anomaly to ensure it doesn't effect count of false positive
    monkeypatch.setenv("CUSTOMER_ID", str(uuid.uuid4()))
    response = test_client.post('/api/feedback', json=generate_feedback())
    assert response.status_code == 200

    # Renew ids for second anomaly feedback
    monkeypatch.setenv("CUSTOMER_ID", str(uuid.uuid4()))
    response = test_client.post('/api/feedback', json=generate_feedback("True"))
    assert response.status_code == 200

    response = test_client.get('/api/false_positive')
    expected_number_of_anomalies = number_of_anomalies + 1
    assert count_feedback(response) == expected_number_of_anomalies


def test_get_feedback_exception(test_client, monkeypatch):
    """Test if appropriate status codes are returned upon exceptions."""
    # Test if an error is appropriately returned when a required key is missing
    monkeypatch.setenv("CUSTOMER_ID", str(uuid.uuid4()))
    req = generate_feedback("True")
    del req['is_anomaly']
    response = test_client.post('/api/feedback', json=req)
    assert response.status_code == 500

    # Test if an error is appropriately returned when a required key is empty
    monkeypatch.setenv("CUSTOMER_ID", str(uuid.uuid4()))
    req = generate_feedback("True")
    req['is_anomaly'] = ""
    response = test_client.post('/api/feedback', json=req)
    assert response.status_code == 500
