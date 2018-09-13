"""
"""

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
        configuration.storage = LSConfiguration()

    def retrieve(self, time_range, number_of_entries):
        """Retrieve data from local storage."""
        data = []
        _LOGGER.info("Reading from %s" % self.config.storage.LS_INPUT_PATH)
        if self.config.storage.LS_INPUT_PATH == "-":
            cnt = 0
            for line in self._stdin():
                try:
                    data.append(json.loads(line))
                except ValueError as ex:
                    _LOGGER.error("Parsing failed (%s), assuming plain text" % ex)
                    data.append({'_source': {'message': str(line)}})
                cnt += 1
                if cnt >= number_of_entries:
                    break

            # only use _source sub-dict
            data = [x['_source'] for x in data]
            data_set = json_normalize(data)
        else:
            with open(self.config.storage.LS_INPUT_PATH, 'r') as fp:
                data = json.load(fp)

            data_set = json_normalize(data)

            if len(data_set) > number_of_entries:
                data_set = data_set[:-number_of_entries]
        _LOGGER.info("%d logs loaded", len(data_set))

        # Prepare data for training/inference
        self._preprocess(data_set)

        return data_set, data

    def store_results(self, data):
        """Store results."""
        if len(self.config.storage.LS_OUTPUT_PATH) > 0:
            with open(self.config.storage.LS_OUTPUT_PATH, 'a') as fp:
                json.dump(data, fp)
        else:
            for item in data:
                _LOGGER.info("Anomaly: %d, Anmaly score: %f" % (item['anomaly'], item['anomaly_score']))

    @classmethod
    def _stdin(cls):
        while True:
            line = sys.stdin.readline()
            if not line:
                continue
            stripped = line.strip()
            if len(stripped):
                yield line.strip()


class LSConfiguration(Configuration):
    """Configuration for local storage."""

    # Path to a file containing input data. If the value is '-' the input is expected on STDIN
    LS_INPUT_PATH = ""
    # Path to a file where the results will be stored. Results will be printed to STDOUT if empty
    LS_OUTPUT_PATH = ""

    def __init__(self):
        """Initialize configuration."""
        self.load()
