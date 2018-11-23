import pytest

from anomaly_detector.anomaly_detector import AnomalyDetector
import sys
import logging

from anomaly_detector.config import Configuration

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
_LOGGER.addHandler(sh)

w2v_logger = logging.getLogger('gensim.models')
w2v_logger.setLevel(logging.ERROR)

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    _LOGGER.info("Starting...")
    config = Configuration(CONFIGURATION_PREFIX)
    anomaly_detector = AnomalyDetector(config)
    return anomaly_detector

def test_end2endtraining(detector):
    """
    Test_End2EndTraining

    Test anomaly detection training on public dataset to confirm that the training completes successfully end2end

    """
    assert detector.train() == 0


