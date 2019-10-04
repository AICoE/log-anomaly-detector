"""Validates if training was successful."""
import pytest

from anomaly_detector.adapters import SomModelAdapter, SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.jobs import SomTrainJob, SomInferenceJob
from anomaly_detector.storage.local_storage import DefaultStorageAttribute

CONFIGURATION_PREFIX = "LAD"
NUM_LOG_LINES = 812


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml="config_files/.env_local_dir.yaml")
    return config


def test_local_dir_ingest_retrieve(config):
    """Test anomaly detection training on public dataset."""
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    data, dataset = storage_adapter.storage.retrieve(DefaultStorageAttribute())
    print(len(data))
    assert len(data) == NUM_LOG_LINES


def test_training_local_dir(config):
    """Test anomaly detection training on public dataset."""
    model_adapter = SomModelAdapter(SomStorageAdapter(config=config, feedback_strategy=None))
    tc_train = SomTrainJob(node_map=2, model_adapter=model_adapter, recreate_model=True)
    result, dist = tc_train.execute()
    assert result == 0
    model_adapter = SomModelAdapter(SomStorageAdapter(config=config, feedback_strategy=None))
    tc_infer = SomInferenceJob(model_adapter=model_adapter, sleep=False)
    result = tc_infer.execute()
    assert result == 0
