"""For all tasks that run in log anomaly detector you should implement the steps involved in train/infer of models."""
import datetime
import logging
from abc import ABCMeta, abstractmethod
import time
from prometheus_client import Counter

from anomaly_detector.adapters import FeedbackStrategy, SomModelAdapter, SomStorageAdapter
from anomaly_detector.exception import EmptyDataSetException
from anomaly_detector.storage import KafkaSink
import time
from jaeger_client import Config
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
        """Initializing properties for training."""
        self.node_map = node_map
        self.model_adapter = model_adapter
        self.recreate_model = recreate_model

    def execute_with_tracing(self, tracer):
        """Train models for anomaly detection with tracing enabled."""
        with tracer.start_span('aiops_train_execute', child_of=get_current_span()) as span:
            with span_in_context(span):
                return self.execute()

    def execute(self):
        """Train models for anomaly detection."""
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
        """Initialize inference command."""
        self.model_adapter = model_adapter
        self.sleep = sleep
        self.recreate_model = recreate_model

    def execute_with_tracing(self, tracer):
        """Will retrain with fresh data and perform predictions in batches."""
        with tracer.start_span('aiops_inference_execute', child_of=get_current_span()) as span:
            with span_in_context(span):
                return self.execute()

    def execute(self):
        """Execute inference steps and loop."""
        self.model_adapter.load_w2v_model()
        self.model_adapter.load_som_model()
        mean, threshold = self.model_adapter.set_threshold()
        infer_loops = 0
        while infer_loops < self.model_adapter.storage_adapter.INFER_LOOPS:
            INFER_COUNT.inc()
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
            # This is for offline testing of the ML Training and Infer which results in trigger emails.
            if self.model_adapter.storage_adapter.PREDICTION_ALERT is True:
                if self.model_adapter.storage_adapter.STORAGE_BACKEND_SINK == "kafka":
                    kf_sink = KafkaSink(config=self.model_adapter.storage_adapter.config)
                    for data in results:
                        kf_sink.store_results(data=data)
                        kf_sink.flush()
                    logging.info("{} predictions sent to kafka".format(len(results)))
                else:
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


class Singleton(type):
    """Singleton ensures that a single instance will exist of this class."""

    def __init__(self, *args, **kwargs):
        """Create single instance if none exists."""
        self.__state = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Overwriting the call method when this is called."""
        if self.__state is None:
            self.__state = super().__call__(*args, **kwargs)
            return self.__state
        else:
            return self.__state


class Pipeline(metaclass=Singleton):
    """Pipeline is will add steps to a ml pipeline to process."""

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

    def execute_steps(self, tracer=None):
        """Execute steps one by one."""
        for step in self.steps:
            if tracer is None:
                step.execute()
            else:
                step.execute_with_tracing(tracer)
            self.count += 1

    def __len__(self):
        """Number of steps in queue."""
        return len(self.steps)

    def clear(self):
        """Reset the values."""
        self.steps = []
        self.count = 0


class PipelineCatalog(object):
    """Model Catalog for selecting which MLModel To Use for Anomaly Detection."""

    def __init__(self, config, feedback_strategy, job):
        """Pipeline initialization logic."""
        self.config = config
        self.feedback_strategy = feedback_strategy
        if job in self._class_method_choices:
            self.job = job
        else:
            raise ValueError("Unsupported job used {}".format(job))

    @classmethod
    def create_sompy_modeladapter(cls, config, feedback_strategy):
        """Setup sompy model adapter which provides functionality required to train SOMPY Model with W2V encoding."""
        if feedback_strategy is None:
            feedback_strategy = FeedbackStrategy(config=config)
        storage_adapter = SomStorageAdapter(config, feedback_strategy)
        model_adapter = SomModelAdapter(storage_adapter)
        return model_adapter

    @classmethod
    def _sompy_train_job(cls, config, feedback_strategy):
        """Perform Training and inference of SOMPY Model."""
        pipeline = Pipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        train = SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter)
        pipeline.add_steps(train)
        return pipeline

    @classmethod
    def _sompy_train_infer_job(cls, config, feedback_strategy):
        """Perform Training and inference of SOMPY Model."""
        pipeline = Pipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        pipeline.add_steps(SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter))
        pipeline.add_steps(SomInferenceJob(model_adapter=model_adapter))
        return pipeline

    @classmethod
    def _sompy_infer_job(cls, config, feedback_strategy):
        """Perform inference of SOMPY Model."""
        pipeline = Pipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        train = SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter)
        pipeline.add_steps(train)
        return pipeline

    _class_method_choices = {'sompy.train': _sompy_train_job,
                             'sompy.inference': _sompy_infer_job,
                             'sompy.train.inference': _sompy_train_infer_job}

    def get_pipeline(self):
        """Pipeline Api api."""
        return self._class_method_choices[self.job].__get__(None, self.__class__)(self.config, self.feedback_strategy)
