CONFIGURATION_PREFIX = "LAD"
import pytest
from anomaly_detector.storage.local_storage import DefaultStorageAttribute
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter

from anomaly_detector.jobs.tasks import SomTrainCommand, SomInferCommand
from anomaly_detector.config import Configuration

@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml="config_files/.env_local_dir.yaml")

    return config


def test_end2endlocalfile(config):
    """Test anomaly detection training on public dataset."""
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    result=storage_adapter.storage.retrieve(DefaultStorageAttribute())
    print("Count: {}".format(len(result)))
    assert True


def test_training_infer(config):
    """Test anomaly detection training on public dataset."""
    model_adapter = SomModelAdapter(SomStorageAdapter(config=config, feedback_strategy=None))
    tc_train = SomTrainCommand(node_map=2, model_adapter=model_adapter, recreate_model=True)
    result, dist = tc_train.execute()
    assert result == 0
    model_adapter = SomModelAdapter(SomStorageAdapter(config=config, feedback_strategy=None))
    tc_infer = SomInferCommand(model_adapter=model_adapter, sleep=False)
    result = tc_infer.execute()
    assert result == 0
