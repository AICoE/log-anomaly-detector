"""Test if SOM can learn from false positives."""
import logging
import pytest
from anomaly_detector.adapters import FeedbackStrategy, SomModelAdapter, SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.core import SomTrainJob

FREQ_NUM = 10000
NODE_MAP = 2
LOG_MSG = "(root) CMD (/usr/local/bin/monitor-apache-stats.sh >/dev/null 2>&1)"


@pytest.mark.core
@pytest.mark.false_positive
def test_false_positive(cnf_100K_events):
    """Testing False Positives and feeding it into the model."""
    freq_one = get_score(cnf_100K_events, NODE_MAP, lambda ctx: [{"message": LOG_MSG}])
    freq_two = get_score(cnf_100K_events, NODE_MAP, lambda ctx: [{"message": LOG_MSG}] * FREQ_NUM)
    logging.info("FREQ = {}, FREQ_TWO = {}".format(freq_one, freq_two))
    assert freq_one > freq_two


def get_score(config, node_map, feedback):
    """Simple utility function for injecting custom mock function into Detector."""
    feedback_strategy = FeedbackStrategy(config, func=feedback)
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=feedback_strategy)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=node_map, model_adapter=model_adapter)
    success, dist = tc.execute()
    freq_one = dist[-1]
    return freq_one
