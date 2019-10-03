"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy
from anomaly_detector.jobs.tasks import TaskQueue, SomTrainCommand, SomInferCommand
from anomaly_detector.exception.exceptions import EmptyDataSetException
import logging
import uuid

import time
from jaeger_client import Config
from opentracing_instrumentation.request_context import get_current_span, span_in_context


class AnomalyDetectorFacade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config, feedback_strategy=None, tracing_enabled=False):
        """Set up required properties to run training or prediction.

        :param config: configuration provided via yaml or environment variables
        :param feedback_strategy: a function that runs to improve the feedback of system
        """
        if feedback_strategy is None:
            feedback_strategy = FeedbackStrategy(config=config)
        storage_adapter = SomStorageAdapter(config, feedback_strategy)
        self.__model_adapter = SomModelAdapter(storage_adapter)
        self.tasks = TaskQueue()
        self.tracing_enabled = tracing_enabled

    def create_tracer(self, service):
        """Initialize tracer for open tracing."""
        logging.getLogger('').handlers = []
        logging.basicConfig(format='%(message)s', level=logging.DEBUG)
        config = Config(
            config={
                'sampler': {
                    'type': 'const',
                    'param': 1,
                },
                'logging': True,
            },
            service_name=service,
        )
        return config.initialize_tracer()

    def run(self, single_run=False):
        """Run train and inference and main event loop.

        :param single_run: if this is set to TRUE then we exit loop after first iteration.
        :return: None
        """
        exit = False

        while exit is False:
            try:
                train = SomTrainCommand(model_adapter=self.__model_adapter)
                infer = SomInferCommand(model_adapter=self.__model_adapter)
                self.tasks.add_steps(train)
                self.tasks.add_steps(infer)
                self.start_job()
                logging.info("Job ran succesfully")
            except EmptyDataSetException as e:
                logging.debug(e)
            finally:
                time.sleep(5)
                exit = single_run

    def start_job(self):
        """Start job to run all steps in workflow."""
        job_id = uuid.uuid4()
        logging.info("Executing job: {}".format(job_id))
        tracer = self.create_tracer('log-anomaly-detection')
        if self.tracing_enabled:
            logging.info("Tracing enabled")
            with tracer.start_span('anomaly_facade_run') as span:
                span.set_tag('job_id', job_id)
                with span_in_context(span):
                    self.tasks.execute_steps(tracer=tracer)
        else:
            self.tasks.execute_steps()

    def train(self, node_map=24):
        """Run training of model and provides size of map.

        :param node_map: by default the node_map is 24 and is custom field for SOM model.
        :return: None
        """
        train = SomTrainCommand(node_map=node_map, model_adapter=self.__model_adapter)
        self.tasks.add_steps(train)
        self.start_job()

    def infer(self):
        """Run inference of model.

        :return: None
        """
        inference = SomInferCommand(model_adapter=self.__model_adapter)
        self.tasks.add_steps(inference)
        self.start_job()
