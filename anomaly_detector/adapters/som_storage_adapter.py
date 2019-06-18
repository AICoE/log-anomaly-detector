"""Som Storage Adapter for interfacing with custom storage for custom application."""
from anomaly_detector.adapters.base_storage_adapter import BaseStorageAdapter
from anomaly_detector.storage.es_storage import ESStorage
from anomaly_detector.storage.local_storage import LocalStorage
from anomaly_detector.config import Configuration
import requests
import logging
import os
import logging

import requests

from anomaly_detector.adapters.base_storage_adapter import BaseStorageAdapter
from anomaly_detector.storage.es_storage import ESStorage
from anomaly_detector.storage.local_storage import LocalStorage

from anomaly_detector.storage.storage_attribute import ESStorageAttribute


class SomStorageAdapter(BaseStorageAdapter):
    """Custom storage interface for dealing with som model."""

    STORAGE_BACKENDS = [LocalStorage, ESStorage]

    def __init__(self, config, feedback_strategy):
        """Initialize configuration for for storage interface."""
        self.config = config
        self.feedback_strategy = feedback_strategy
        for backend in self.STORAGE_BACKENDS:
            if backend.NAME == self.config.STORAGE_BACKEND:
                logging.info("Using %s storage backend" % backend.NAME)
                self.storage = backend(config)
                break
        if not self.storage:
            raise Exception("Could not use %s storage backend" % self.STORAGE_BACKENDS)

    def _load_data(self, time_span, max_entries, false_positives=None):
        """Loading data from storage into pandas dataframe for processing."""
        data, raw = self.storage.retrieve(time_span,
                                          max_entries,
                                          false_positives)
        if len(data) == 0:
            logging.info("There are no logs in last %s seconds", time_span)
            return None, None

    def retrieve_data(self, timespan, max_entry, false_positive):
        """Fetch data from storage system."""
        return self.storage.retrieve(ESStorageAttribute(timespan,
                                                        max_entry,
                                                        false_positive))

    def load_data(self, config_type):
        """Load data from storage class depending on training vs inference."""
        false_data = self.feedback_strategy.execute()
        if config_type == "train":
            return self.retrieve_data(self.config.TRAIN_TIME_SPAN, self.config.TRAIN_MAX_ENTRIES,
                                      false_data)
        elif config_type == "infer":
            return self.retrieve_data(self.config.INFER_TIME_SPAN, self.config.INFER_MAX_ENTRIES,
                                      false_data)
        else:
            raise Exception("Not Supported option . config_type not in ['infer','train']")

    def persist_data(self, df):
        """Abstraction around storage persistence class."""
        self.storage.store_results(df)

    def __getattr__(self, name):
        """Delegate all methods from config as a passthrough proxy into configurations."""
        return getattr(self.config, name)
