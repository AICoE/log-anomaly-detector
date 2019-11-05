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


def test_storage_catalog_local_file_retrieve(cnf_local_500):
    """Test anomaly detection training on public dataset."""
    sc = StorageCatalog(config=cnf_local_500, storage_api="local.source")
    storage: StorageSource = sc.get_storage_api()
    data, dataset = storage.retrieve(DefaultStorageAttribute())
    print(len(data))
    assert len(data) == 512


def test_storage_catalog_local_file_save_data(cnf_local_500):
    """Test anomaly detection training on public dataset."""
    sc = StorageCatalog(config=cnf_local_500, storage_api="local.sink")
    storage: StorageSink = sc.get_storage_api()
    sample_output = {"Results": "False"}
    storage.store_results(sample_output)
    data = None
    with open(cnf_local_500.LS_OUTPUT_PATH) as json_file:
        data = json.load(json_file)
        print(data)
    assert data == sample_output
