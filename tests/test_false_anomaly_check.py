"""Test if SOM can learn from false positives."""
import pytest
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.anomaly_detector_facade import AnomalyDetectorFacade
from anomaly_detector.config import Configuration
import logging
import numpy as np

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def detector():
    """Provide default configurations to load yaml instead of env var."""
    config = Configuration(prefix=CONFIGURATION_PREFIX,
                           config_yaml=".test_env_config.yaml")
    anomaly_detector = AnomalyDetectorFacade(config)
    return anomaly_detector


def test_false_positive(detector):
    """Testing False Positives and feeding it into the model."""
    false_positives = [{"message": "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"}]
    false_positives2 = [{"message": "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"}] * 10000
    success, dist = detector.train(node_map=2, false_positives=false_positives)
    logging.info(np.mean(dist), np.std(dist), np.max(dist), np.min(dist))
    freq_one = dist[-1]
    success, dist = detector.train(node_map=2, false_positives=false_positives2)
    logging.info(np.mean(dist), np.std(dist), np.max(dist), np.min(dist))
    freq_two = dist[-1]
    logging.info("FREQ = {}, FREQ_TWO = {}".format(freq_one, freq_two))
    assert freq_one > freq_two
