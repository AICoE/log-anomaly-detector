"""Validates if training was successful."""
import pytest
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    """Initialize configurations before testing."""
    # prefix=None, config_yaml=None):
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml=".env_config.yaml")
    anomaly_detector = AnomalyDetector(config)
    return anomaly_detector


def test_end2endtraining(detector):
    """Test anomaly detection training on public dataset."""
    data, json_logs = detector.fetch_data()
    result, dist = detector.train(data=data)
    assert result == 0
