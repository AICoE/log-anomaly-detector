"""Tasks scheduled to be executed for log anomaly detector are provided here in the form of commands."""
from anomaly_detector.jobs.core import AbstractCommand, SomTrainJob,\
    SomInferenceJob, Singleton, Pipeline

__all__ = ['AbstractCommand',
           'SomTrainJob',
           'SomInferenceJob',
           'Singleton',
           'Pipeline']
