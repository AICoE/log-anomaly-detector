"""DetectorPipeline class for processing a workflow of tasks to train an ML model."""
from anomaly_detector.core import AbstractCommand
from anomaly_detector.adapters import FeedbackStrategy, SomStorageAdapter, SomModelAdapter
from anomaly_detector.core import SomTrainJob, SomInferenceJob
from prometheus_client import Counter

DETECTOR_PIPELINE_COUNTER = Counter("aiops_lad_pipeline_run_count",
                                    "Count of how many times data pipeline gets executed")


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


class DetectorPipeline(metaclass=Singleton):
    """Detector Pipeline allows for adding steps needed to go from dataset to prediction."""

    def __init__(self):
        """Initialize detector pipeline with count of zero and no steps to execute."""
        self.count = 0
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
            DETECTOR_PIPELINE_COUNTER.inc()
            self.count += 1

    def __len__(self):
        """Number of steps in queue."""
        return len(self.steps)

    def clear(self):
        """Reset the values."""
        self.steps = []
        self.count = 0


class DetectorPipelineCatalog(object):
    """Model Catalog for selecting which MLModel To Use for Anomaly Detection."""

    def __init__(self, config, feedback_strategy, job):
        """Detector Pipeline Catalog initialization logic."""
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
        pipeline = DetectorPipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        train = SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter)
        pipeline.add_steps(train)
        return pipeline

    @classmethod
    def _sompy_train_infer_job(cls, config, feedback_strategy):
        """Perform Training and inference of SOMPY Model."""
        pipeline = DetectorPipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        pipeline.add_steps(SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter))
        pipeline.add_steps(SomInferenceJob(model_adapter=model_adapter))
        return pipeline

    @classmethod
    def _sompy_infer_job(cls, config, feedback_strategy):
        """Perform inference of SOMPY Model."""
        pipeline = DetectorPipeline()
        model_adapter = cls.create_sompy_modeladapter(config, feedback_strategy)
        train = SomTrainJob(node_map=config.SOMPY_NODE_MAP, model_adapter=model_adapter)
        pipeline.add_steps(train)
        return pipeline

    _class_method_choices = {'sompy.train': _sompy_train_job,
                             'sompy.inference': _sompy_infer_job,
                             'sompy.train.inference': _sompy_train_infer_job}

    def get_pipeline(self):
        """Provide a pipeline to allow client to select which algorithm to use."""
        return self._class_method_choices[self.job].__get__(None, self.__class__)(self.config, self.feedback_strategy)
