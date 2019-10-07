"""Som Storage Adapter for interfacing with custom storage for custom application."""
import logging
from anomaly_detector.adapters import BaseStorageAdapter
from anomaly_detector.decorator.utils import latency_logger
from anomaly_detector.storage import ESStorageAttribute
from anomaly_detector.storage.storage_proxy import StorageProxy


class SomStorageAdapter(BaseStorageAdapter):
    """Custom storage interface for dealing with som model."""

    def __init__(self, config, feedback_strategy=None):
        """Initialize configuration for for storage interface."""
        self.config = config
        self.feedback_strategy = feedback_strategy
        self.storage = StorageProxy(config)

    def retrieve_data(self, timespan, max_entry, false_positive):
        """Fetch data from storage system."""
        data, raw = self.storage.retrieve(ESStorageAttribute(timespan,
                                                             max_entry,
                                                             false_positive))
        if len(data) == 0:
            logging.info("There are no logs in last %s seconds", timespan)
            return None, None
        else:
            return data, raw

    @latency_logger(name="SomStorageAdapter")
    def load_data(self, config_type):
        """Load data from storage class depending on training vs inference."""
        false_data = None
        if self.feedback_strategy is not None:
            false_data = self.feedback_strategy.execute()

        if config_type == "train":
            return self.retrieve_data(timespan=self.config.TRAIN_TIME_SPAN,
                                      max_entry=self.config.TRAIN_MAX_ENTRIES,
                                      false_positive=false_data)
        elif config_type == "infer":
            return self.retrieve_data(timespan=self.config.INFER_TIME_SPAN,
                                      max_entry=self.config.INFER_MAX_ENTRIES,
                                      false_positive=false_data)
        else:
            raise Exception("Not Supported option . config_type not in ['infer','train']")

    @latency_logger(name="SomStorageAdapter")
    def persist_data(self, df):
        """Abstraction around storage persistence class."""
        self.storage.store_results(df)

    def __getattr__(self, name):
        """Delegate all methods from config as a passthrough proxy into configurations."""
        return getattr(self.config, name)
