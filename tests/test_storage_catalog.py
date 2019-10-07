"""Test storage catalog ability to read and write data."""
import pytest

from anomaly_detector.config import Configuration
from anomaly_detector.storage.local_storage import DefaultStorageAttribute
from anomaly_detector.storage.storage_catalog import StorageCatalog
from anomaly_detector.storage.storage_source import StorageSource
from anomaly_detector.storage.storage_sink import StorageSink
import json

CONFIGURATION_PREFIX = "LAD"
NUM_LOG_LINES = 812


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration()
    config.STORAGE_BACKEND = "local"
    config.LS_INPUT_PATH = "validation_data/orders-500.log"
    config.LS_OUTPUT_PATH = "validation_data/results-oct4.1.txt"
    return config


def test_storage_catalog_local_file_retrieve(config):
    """Test anomaly detection training on public dataset."""
    sc = StorageCatalog(config=config, storage_api="local.source")
    storage: StorageSource = sc.get_storage_api()
    data, dataset = storage.retrieve(DefaultStorageAttribute())
    print(len(data))
    assert len(data) == 512


def test_storage_catalog_local_file_save_data(config):
    """Test anomaly detection training on public dataset."""
    sc = StorageCatalog(config=config, storage_api="local.sink")
    storage: StorageSink = sc.get_storage_api()
    sample_output = {"Results": "False"}
    storage.store_results(sample_output)
    data = None
    with open(config.LS_OUTPUT_PATH) as json_file:
        data = json.load(json_file)
        print(data)
    assert data == sample_output
