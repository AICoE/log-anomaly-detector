"""Local Storage."""
from anomaly_detector.storage.storage_attribute import DefaultStorageAttribute
from pandas.io.json import json_normalize
import json
import sys

from .storage import Storage
from ..config import Configuration

import logging

_LOGGER = logging.getLogger(__name__)


class LocalStorage(Storage):
    """Local storage implementation."""

    NAME = "local"

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    def retrieve(self, storage_attribute: DefaultStorageAttribute):
        """Retrieve data from local storage."""
        data = []
        _LOGGER.info("Reading from %s" % self.config.LS_INPUT_PATH)

        data, data_set = self.read_file(self.config.LS_INPUT_PATH, storage_attribute)
        # Prepare data for training/inference
        self._preprocess(data_set)
        return [(data_set, data)]

    def read_file(self, filepath, storage_attribute):
        """Read and parse files."""
        data = []
        with open(filepath, "r") as fp:
            if self.config.LS_INPUT_PATH.endswith("json"):
                data = json.load(fp)
            else:
                # Here we are loading in data from common log format Columns [0]= timestamp [1]=severity [2]=msg
                for line in fp:
                    message_field = self.extract_message(line)
                    data.append({"message": message_field})
            # TODO: Make sure to check for false_data is not Null
            if storage_attribute.false_data is not None:
                data.extend(storage_attribute.false_data)
        data_set = json_normalize(data)
        _LOGGER.info("%d logs loaded", len(data_set))
        return data, data_set

    def extract_message(self, line):
        """Parse common log file format."""
        message_field = " ".join(line.split(" ")[2:])
        message_field = message_field.rstrip("\n")
        return message_field

    def store_results(self, data):
        """Store results."""
        if len(self.config.LS_OUTPUT_PATH) > 0:
            with open(self.config.LS_OUTPUT_PATH, self.config.LS_OUTPUT_RWA_MODE) as fp:
                json.dump(data, fp)
        else:
            for item in data:
                _LOGGER.info("Anomaly: %d, Anmaly score: %f" % (item["anomaly"], item["anomaly_score"]))
