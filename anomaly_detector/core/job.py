"""For all tasks that run in log anomaly detector you should implement the steps involved in train/infer of models."""
import datetime
import logging
from abc import ABCMeta, abstractmethod
from prometheus_client import Counter
from anomaly_detector.exception import EmptyDataSetException
import time
from opentracing_instrumentation.request_context import get_current_span, span_in_context

TRAINING_COUNT = Counter("aiops_lad_train_count", "count of training runs")
INFER_COUNT = Counter("aiops_lad_inference_count", "count of inference runs")


class AbstractCommand(metaclass=ABCMeta):
    """Generic command that gets executed when added to the TaskManager steps."""

    @abstractmethod
    def execute(self):
        """Generic method that gets executed by the task manager."""
        raise NotImplementedError("Please implement the <execute method>")


class SomTrainJob(AbstractCommand):
    """Som Training logic custom for each model. For this model we need to setup some configs."""

    recreate_models = False

    def __init__(self, node_map=24, model_adapter=None, recreate_model=True):
        """Initialize training job with fields to perform model training."""
        self.node_map = node_map
        self.model_adapter = model_adapter
        self.recreate_model = recreate_model

    def execute_with_tracing(self, tracer):
        """Wrap execution of train with tracer to measure latency."""
        with tracer.start_span('aiops_train_execute', child_of=get_current_span()) as span:
            with span_in_context(span):
                return self.execute()

    def execute(self):
        """Execute training logic for anomaly detection for SOMPY with w2v encoding."""
        TRAINING_COUNT.inc()
        dataframe, raw_data = self.model_adapter.preprocess(config_type="train",
                                                            recreate_model=self.recreate_model)
        if not raw_data:
            raise EmptyDataSetException("no new logs found.")
        # After first time training we will only update w2v model not recreate it everytime.
        dist = self.model_adapter.train(node_map=self.node_map, data=dataframe, recreate_model=self.recreate_model)
        self.recreate_model = False
        return 0, dist


class SomInferenceJob(AbstractCommand):
    """Som Inference implementation."""

    def __init__(self, model_adapter=None, sleep=True, recreate_model=False):
        """Initialize inference job with fields to perform model inference."""
        self.model_adapter = model_adapter
        self.sleep = sleep
        self.recreate_model = recreate_model

    def execute_with_tracing(self, tracer):
        """Will wrap execution of inference with tracer to measure latency."""
        with tracer.start_span('aiops_inference_execute', child_of=get_current_span()) as span:
            with span_in_context(span):
                return self.execute()

    def execute(self):
        """Execute inference logic for SOMPY with W2V encoding."""
        self.model_adapter.load_w2v_model()
        self.model_adapter.load_som_model()
        mean, threshold = self.model_adapter.set_threshold()
        infer_loops = 0
        while infer_loops < self.model_adapter.storage_adapter.INFER_LOOPS:
            then = time.time()
            INFER_COUNT.inc()
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
