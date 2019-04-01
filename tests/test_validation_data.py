import pytest
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    config = Configuration(CONFIGURATION_PREFIX)
    anomaly_detector = AnomalyDetector(config)
    return anomaly_detector


def test_end2endtraining(detector):
    """
    Test_End2EndTraining

    Test anomaly detection training on public dataset to confirm that the training completes successfully end2end

    """
    assert detector.train() == 0
