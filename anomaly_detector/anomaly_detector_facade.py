"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy
from anomaly_detector.jobs.tasks import TaskQueue, SomTrainCommand, SomInferCommand
from prometheus_client import start_http_server
import time


class AnomalyDetectorFacade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config, feedback_strategy=None):
        """Abstraction around model adapter run method."""
        if feedback_strategy is None:
            feedback_strategy = FeedbackStrategy(config=config)
        storage_adapter = SomStorageAdapter(config, feedback_strategy)
        self.__model_adapter = SomModelAdapter(storage_adapter)
        self.mgr = TaskQueue()

    def run(self, single_run=False):
        """Abstraction around model adapter run method."""
        start_http_server(8081)
        break_out = False
        while break_out is False:
            train = SomTrainCommand(model_adapter=self.__model_adapter)
            infer = SomInferCommand(model_adapter=self.__model_adapter)
            self.mgr.add_steps(train)
            self.mgr.add_steps(infer)
            self.mgr.execute_steps()
            print("log::facade::run")
            time.sleep(5)
            break_out = single_run

    def train(self, node_map=24):
        """Abstraction around model adapter train method."""
        tc = SomTrainCommand(node_map=node_map, model_adapter=self.__model_adapter)
        self.mgr.add_steps(tc)
        self.mgr.execute_steps()

    def infer(self):
        """Abstraction around model adapter inference method."""
        tc_infer = SomInferCommand(model_adapter=self.__model_adapter)
        self.mgr.add_steps(tc_infer)
        self.mgr.execute_steps()
