"""Anomaly Detector Facade - Acts as a gateway and abstracts the complexity."""
from anomaly_detector.core import DetectorPipeline, DetectorPipelineCatalog
from anomaly_detector.exception.exceptions import EmptyDataSetException
from anomaly_detector.config import Configuration
from anomaly_detector.adapters.feedback_strategy import FeedbackStrategy
import logging
import uuid

import time
from jaeger_client import Config
from opentracing_instrumentation.request_context import span_in_context


class Facade:
    """For external interface for integration different adapters for custom models and training logic."""

    def __init__(self, config: Configuration, feedback_strategy: FeedbackStrategy = None,
                 tracing_enabled: bool = False):
        """Set up required properties to run training or prediction.

        :param config: configuration provided via yaml or environment variables
        :param feedback_strategy: a function that runs to improve the feedback of system
        """
        self.config = config
        self.feedback_strategy = feedback_strategy
        self.pipeline = DetectorPipeline()
        self.tracing_enabled = tracing_enabled

    @staticmethod
    def create_tracer(service):
        """Initialize tracer for open tracing.

        :param service: service name to use for tracing this application.
        :return: Tracer(opentracing.Tracer)
        """
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

    def run(self, single_run: bool = False):
        """Run train and inference and main event loop.

        :param single_run: if this is set to TRUE then we exit loop after first iteration.
        :return: None
        """
        exit = False
        while exit is False:
            try:
                jobs = DetectorPipelineCatalog(config=self.config,
                                               feedback_strategy=self.feedback_strategy,
                                               job="sompy.train.inference")
                self.pipeline = jobs.get_pipeline()
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
                    self.pipeline.execute_steps(tracer=tracer)
        else:
            self.pipeline.execute_steps()

    def train(self):
        """Run training of model and provides size of map.

        :return: None
        """
        jobs = DetectorPipelineCatalog(config=self.config,
                                       feedback_strategy=self.feedback_strategy,
                                       job="sompy.train")

        self.pipeline = jobs.get_pipeline()
        self.start_job()

    def infer(self):
        """Run inference of model.

        :return: None
        """
        jobs = DetectorPipelineCatalog(config=self.config,
                                       feedback_strategy=self.feedback_strategy,
                                       job="sompy.inference")
        self.pipeline = jobs.get_pipeline()
        self.start_job()
