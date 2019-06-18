"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.config import Configuration


class AnomalyDetectorFacade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config):
        """Abstraction around model adapter run method."""
        storage_adapter = SomStorageAdapter(config)
        self.__model_adapter = SomModelAdapter(storage_adapter)

    def run(self, single_run=False):
        """Abstraction around model adapter run method."""
        self.__model_adapter.run(single_run=single_run)

    def train(self, node_map=24, false_positives=None):
        """Abstraction around model adapter train method."""
        return self.__model_adapter.train(node_map, false_positives)

    def infer(self, false_positives=None):
        """Abstraction around model adapter inference method."""
        return self.__model_adapter.infer(false_positives)
