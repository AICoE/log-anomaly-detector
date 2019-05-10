"""Test if SOM can learn from false positives."""
import pytest
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration
import logging
import numpy as np

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    """Provide default configurations to load yaml instead of env var."""
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml=".test_env_config.yaml")
    anomaly_detector = AnomalyDetector(config)
    return anomaly_detector


def test_false_positive(detector):
    """Testing False Positives and feeding it into the model."""
    fp = [{"message": "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"}]
    fp2 = [{"message": "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"}] * 10000
    success, dist = detector.train(fp=fp, node_map=2)
    logging.info(np.mean(dist), np.std(dist), np.max(dist), np.min(dist))
    freq_one = dist[-1]
    success, dist = detector.train(fp=fp2, node_map=2)
    logging.info(np.mean(dist), np.std(dist), np.max(dist), np.min(dist))
    freq_two = dist[-1]
    logging.info("FREQ = {}, FREQ_TWO = {}".format(freq_one, freq_two))
    assert freq_one > freq_two
