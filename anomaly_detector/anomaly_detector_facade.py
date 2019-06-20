"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy


class AnomalyDetectorFacade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config, feedback_strategy=None):
        """Abstraction around model adapter run method."""
        if feedback_strategy is None:
            feedback_strategy = FeedbackStrategy(config=config)
        storage_adapter = SomStorageAdapter(config, feedback_strategy)
        self.__model_adapter = SomModelAdapter(storage_adapter)

    def run(self, single_run=False):
        """Abstraction around model adapter run method."""
        self.__model_adapter.run(single_run=single_run)

    def train(self, node_map=24):
        """Abstraction around model adapter train method."""
        return self.__model_adapter.train(node_map)

    def infer(self):
        """Abstraction around model adapter inference method."""
        return self.__model_adapter.infer()
