"""Local Storage."""
import json
import logging
from enum import Enum
from pathlib import Path
from anomaly_detector.exception import FileFormatNotSupported
from anomaly_detector.storage.storage_attribute import DefaultStorageAttribute
from anomaly_detector.storage.storage_source import StorageSource
from anomaly_detector.storage.storage import DataCleaner
from collections import deque
from pandas.io.json import json_normalize

_LOGGER = logging.getLogger(__name__)


class LocalDirStorage:
    """Local storage implementation."""

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    class ALLOWED_FILE_FORMATS(Enum):
        """Current Supported file formats that are supported to process."""

        COMMON_LOG = "common_log"
        JSON = "json"


class LocalDirectoryStorageDataSource(StorageSource, DataCleaner, LocalDirStorage):
    """Local storage Data source implementation."""

    NAME = "localdir.source"

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    def get_filesnames_recursively(self, root_path, *, file_ext='log', file_format='common_log'):
        """Setup file read processing."""
        if file_format not in (self.ALLOWED_FILE_FORMATS.COMMON_LOG.value, self.ALLOWED_FILE_FORMATS.JSON.value):
            raise FileFormatNotSupported("File format {} is not supported".format(file_format))
        self.files = [filename for filename in Path(root_path).glob('**/*.{}'.format(file_ext))]

    def retrieve(self, storage_attribute: DefaultStorageAttribute):
        """Retrieve data from local storage."""
        _LOGGER.info("Reading from %s" % self.config.LS_INPUT_PATH)
        return self.read_all_files(storage_attribute)

    def read_file(self, filepath, storage_attribute):
        """Check if file is supported and loop parse each file."""
        data = []
        with open(filepath, "r") as fp:
            if filepath.suffix == ".json":
                data = json.load(fp)
            elif filepath.suffix == ".log":
                # Here we are loading in data from common log format Columns [0]= timestamp [1]=severity [2]=msg
                for line in fp:
                    message_field = self.extract_message(line)
                    data.append({"message": message_field})
            else:
                raise FileFormatNotSupported(
                    "File format is not supported json and common log format (which ends with '.log') .")
            if storage_attribute.false_data is not None:
                data.extend(storage_attribute.false_data)
        return data

    def read_all_files(self, storage_attribute: DefaultStorageAttribute):
        """Loop through all files in directory and send it to parser."""
        self.get_filesnames_recursively(self.config.LS_INPUT_PATH)
        q = deque()
        for file in self.files:
            data = self.read_file(file, storage_attribute)
            q.extend(data)
        dataset = json_normalize(list(q))
        _LOGGER.info("%d logs loaded", len(dataset))
        self._preprocess(dataset)
        return dataset, list(q)

    def extract_message(self, line):
        """Parse common log file format."""
        message_field = " ".join(line.split(" ")[2:])
        message_field = message_field.rstrip("\n")
        return message_field
