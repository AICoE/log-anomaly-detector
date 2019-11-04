"""Local Storage."""
from anomaly_detector.storage.storage_attribute import DefaultStorageAttribute
from pandas.io.json import json_normalize
from anomaly_detector.storage.storage_sink import StorageSink
from anomaly_detector.storage.storage_source import StorageSource
from anomaly_detector.storage.storage import DataCleaner
import logging
import json

_LOGGER = logging.getLogger(__name__)


class LocalStorageDataSink(StorageSink, DataCleaner):
    """Local storage data sink implementation."""

    NAME = "local.sink"

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    def store_results(self, data):
        """Store results."""
        if len(self.config.LS_OUTPUT_PATH) > 0:
            with open(self.config.LS_OUTPUT_PATH, self.config.LS_OUTPUT_RWA_MODE) as fp:
                json.dump(data, fp)
        else:
            for item in data:
                _LOGGER.info("Anomaly: %d, Anmaly score: %f" % (item["anomaly"], item["anomaly_score"]))


class LocalStorageDataSource(StorageSource, DataCleaner):
    """Local storage Data source implementation."""

    NAME = "local.source"

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    def retrieve(self, storage_attribute: DefaultStorageAttribute):
        """Retrieve data from local storage."""
        data = []
        _LOGGER.info("Reading from %s" % self.config.LS_INPUT_PATH)

        with open(self.config.LS_INPUT_PATH, "r") as fp:
            if self.config.LS_INPUT_PATH.endswith("json"):
                data = json.load(fp)
            else:
                # Here we are loading in data from common log format Columns [0]= timestamp [1]=severity [2]=msg
                for line in fp:
                    message_field = " ".join(line.split(" ")[2:])
                    message_field = message_field.rstrip("\n")
                    data.append({"message": message_field})
            if storage_attribute.false_data is not None:
                data.extend(storage_attribute.false_data)
        data_set = json_normalize(data)
        _LOGGER.info("%d logs loaded", len(data_set))
        self._preprocess(data_set)
        return data_set, data
