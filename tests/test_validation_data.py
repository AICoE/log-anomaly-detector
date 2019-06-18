"""Validates if training was successful."""
import pytest
from anomaly_detector.anomaly_detector_facade import AnomalyDetectorFacade
from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    """Initialize configurations before testing."""
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml=".env_config.yaml")
    anomaly_detector = AnomalyDetectorFacade(config)
    return anomaly_detector


def test_end2endtraining(detector):
    """Test anomaly detection training on public dataset."""
    result, dist = detector.train()
    assert result == 0
