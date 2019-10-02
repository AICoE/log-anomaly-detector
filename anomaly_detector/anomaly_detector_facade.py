"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy
from anomaly_detector.jobs.tasks import TaskQueue, SomTrainCommand, SomInferCommand
from anomaly_detector.exception.exceptions import EmptyDataSetException
import logging


import time


class AnomalyDetectorFacade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config, feedback_strategy=None):
        """Set up required properties to run training or prediction.

        :param config: configuration provided via yaml or environment variables
        :param feedback_strategy: a function that runs to improve the feedback of system
        """
        if feedback_strategy is None:
            feedback_strategy = FeedbackStrategy(config=config)
        storage_adapter = SomStorageAdapter(config, feedback_strategy)
        self.__model_adapter = SomModelAdapter(storage_adapter)
        self.tasks = TaskQueue()

    def run(self, single_run=False):
        """Run train and inference and main event loop.

        :param single_run: if this is set to TRUE then we exit loop after first iteration.
        :return: None
        """
        exit = False
        train = SomTrainCommand(model_adapter=self.__model_adapter)
        infer = SomInferCommand(model_adapter=self.__model_adapter)
        self.tasks.add_steps(train)
        self.tasks.add_steps(infer)
        while exit is False:
            try:
                self.tasks.execute_steps()
                logging.info("Job ran succesfully")
            except EmptyDataSetException as e:
                logging.debug(e)
            finally:
                time.sleep(5)
                exit = single_run

    def train(self, node_map=24):
        """Run training of model and provides size of map.

        :param node_map: by default the node_map is 24 and is custom field for SOM model.
        :return: None
        """
        train = SomTrainCommand(node_map=node_map, model_adapter=self.__model_adapter)
        self.tasks.add_steps(train)
        self.tasks.execute_steps()

    def infer(self):
        """Run inference of model.

        :return: None
        """
        inference = SomInferCommand(model_adapter=self.__model_adapter)
        self.tasks.add_steps(inference)
        self.tasks.execute_steps()
