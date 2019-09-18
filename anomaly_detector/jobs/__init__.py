"""Tasks scheduled to be executed for log anomaly detector are provided here in the form of commands."""
from anomaly_detector.jobs.tasks import AbstractCommand, SomTrainCommand,\
    SomInferCommand, Singleton, TaskQueue

__all__ = ['AbstractCommand',
           'SomTrainCommand',
           'SomInferCommand',
           'Singleton',
           'TaskQueue']
