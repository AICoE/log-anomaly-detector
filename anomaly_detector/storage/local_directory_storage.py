"""Local Storage."""
from anomaly_detector.storage.storage_attribute import DefaultStorageAttribute
from anomaly_detector.storage.local_storage import LocalStorage
from pandas.io.json import json_normalize
import json
from pathlib import Path
from enum import Enum
from anomaly_detector.exception import FileFormatNotSupported
import logging

_LOGGER = logging.getLogger(__name__)


class LocalDirStorage(LocalStorage):
    """Local storage implementation."""

    NAME = "localdir"

    def __init__(self, configuration):
        """Initialize local storage backend."""
        self.config = configuration

    class ALLOWED_FILE_FORMATS(Enum):
        """Current Supported file formats that are supported to process."""

        COMMON_LOG = "common_log"
        JSON = "json"

    def get_filesnames_recursively(self, root_path, *, file_ext='log', file_format='common_log'):
        """Setup file read processing."""
        self.root_path = root_path
        self.file_ext = file_ext
        self.file_format = file_format
        if file_format not in (self.ALLOWED_FILE_FORMATS.COMMON_LOG.value, self.ALLOWED_FILE_FORMATS.JSON.value):
            raise FileFormatNotSupported("File format {} is not supported".format(file_format))
        self.files = [filename for filename in Path(root_path).glob('**/*.{}'.format(self.file_ext))]

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
        data_set = json_normalize(data)
        _LOGGER.info("%d logs loaded", len(data_set))
        return data, data_set

    def read_all_files(self, storage_attribute: DefaultStorageAttribute):
        """Loop through all files in directory and send it to parser."""
        self.get_filesnames_recursively(self.config.LS_INPUT_PATH)
        items = []
        for file in self.files:
            data, data_set = self.read_file(file, storage_attribute)
            self._preprocess(data_set)
            items.append((data, data_set))
        return items
