"""For all tasks that run in log anomaly detector you should implement the steps involved in train/infer of models."""
import datetime
import logging
from abc import ABCMeta, abstractmethod
import time


class AbstractCommand(metaclass=ABCMeta):
    """Generic command that gets executed when added to the TaskManager steps."""

    @abstractmethod
    def execute(self):
        """Generic method that gets executed by the task manager."""
        raise NotImplementedError("Please implement the <execute method>")


class SomTrainCommand(AbstractCommand):
    """Som Training logic custom for each model. For this model we need to setup some configs."""

    recreate_models = False

    def __init__(self, node_map=24, model_adapter=None, recreate_model=True):
        """Initializing properties for training."""
        self.node_map = node_map
        self.model_adapter = model_adapter
        self.recreate_model = recreate_model

    def execute(self):
        """Train models for anomaly detection."""
        data, _ = self.model_adapter.preprocess(config_type="train",
                                                recreate_model=self.recreate_model)
        # After first time training we will only update w2v model not recreate it everytime.
        dist = self.model_adapter.train(node_map=self.node_map, data=data, recreate_model=self.recreate_model)
        self.recreate_model = False
        return 0, dist


class SomInferCommand(AbstractCommand):
    """Som Inference implementation."""

    def __init__(self, model_adapter=None, sleep=True, recreate_model=False):
        """Initialize inference command."""
        self.model_adapter = model_adapter
        self.sleep = sleep
        self.recreate_model = recreate_model

    def execute(self):
        """Will retrain with fresh data and perform predictions in batches."""
        self.model_adapter.load_w2v_model()
        self.model_adapter.load_som_model()

        mean, threshold = self.model_adapter.set_threshold()
        infer_loops = 0
        while infer_loops < self.model_adapter.storage_adapter.INFER_LOOPS:
            then = time.time()
            now = datetime.datetime.now()
            # Get data for inference
            data, json_logs = self.model_adapter.preprocess(config_type="infer",
                                                            recreate_model=self.recreate_model)
            if data is None:
                time.sleep(5)
                continue
            logging.info("%d logs loaded from the last %d seconds", len(data),
                         self.model_adapter.storage_adapter.INFER_TIME_SPAN)
            results = self.model_adapter.predict(data, json_logs, threshold)
            self.model_adapter.storage_adapter.persist_data(results)
            # Inference done, increase counter
            infer_loops += 1
            now = time.time()
            if self.sleep is True:
                logging.info("waiting for next minute to start...")
                logging.info("press ctrl+c to stop process")
                sleep_time = self.model_adapter.storage_adapter.INFER_TIME_SPAN - (now - then)
                if sleep_time > 0:
                    time.sleep(sleep_time)
        return 0


class TaskQueue:
    """Task manager is a custom."""

    count = 0

    @staticmethod
    def pipe_tasks(self, func, args, *, callback):
        """Callback is optional."""
        if callback is not None:
            return callback(func(args))
        else:
            return func(args)

    def __init__(self):
        """Add steps or functions to be executed."""
        self.steps = []

    def add_steps(self, step):
        """Add tasks to task queue and check if it is an instance of AbstractCommand."""
        if isinstance(step, AbstractCommand):
            self.steps.append(step)
        else:
            raise TypeError()

    def execute_steps(self):
        """Execute steps one by one."""
        for step in self.steps:
            step.execute()
            self.count += 1

    def __len__(self):
        """Number of steps in queue."""
        return len(self.steps)
