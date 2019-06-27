"""Test if SOM can learn from false positives."""
import pytest
from anomaly_detector.anomaly_detector_facade import AnomalyDetectorFacade
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy
from anomaly_detector.config import Configuration
import logging
import numpy as np

FREQ_NUM = 10000
NODE_MAP = 2
LOG_MSG = "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"


@pytest.fixture()
def config():
    """Provide default configurations to load yaml instead of env var."""
    config = Configuration(config_yaml=".test_env_config.yaml")

    return config


def test_false_positive(config):
    """Testing False Positives and feeding it into the model."""
    freq_one = get_score(config, NODE_MAP, lambda ctx: [{"message": LOG_MSG}])
    freq_two = get_score(config, NODE_MAP, lambda ctx: [{"message": LOG_MSG}] * FREQ_NUM)
    logging.info("FREQ = {}, FREQ_TWO = {}".format(freq_one, freq_two))
    assert freq_one > freq_two


def get_score(config, node_map, feedback):
    """Simple utility function for injecting custom mock function into Detector."""
    detector1 = AnomalyDetectorFacade(config, FeedbackStrategy(config, fn=feedback))
    success, dist = detector1.train(node_map)
    logging.info(np.mean(dist), np.std(dist), np.max(dist), np.min(dist))
    freq_one = dist[-1]
    return freq_one
