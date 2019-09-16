CONFIGURATION_PREFIX = "LAD"
import pytest
from anomaly_detector.storage.local_storage import DefaultStorageAttribute
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter

from anomaly_detector.jobs.tasks import SomTrainCommand, SomInferCommand
from anomaly_detector.config import Configuration

from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.jobs.tasks import *


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration(prefix=CONFIGURATION_PREFIX, config_yaml="config_files/.env_local_dir.yaml")

    return config


def test_end2endlocalfile(config):
    """Test anomaly detection training on public dataset."""
    # storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    # # result=storage_adapter.storage.retrieve(DefaultStorageAttribute())
    # mgr = TaskQueue()
    # model_adapter = SomModelAdapter(storage_adapter)
    # tc = SomTrainCommand(node_map=2, model_adapter=model_adapter)
    #
    #
    # mgr.add_steps(tc)
    # mgr.execute_steps()
    # mgr.clear()
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    # result=storage_adapter.storage.retrieve(DefaultStorageAttribute())
    mgr = TaskQueue()

    model_adapter = SomModelAdapter(storage_adapter)
    tc = SomTrainCommand(model_adapter=model_adapter)
    mgr.add_steps(tc)

    tc_infer = SomInferCommand(model_adapter=model_adapter)
    mgr.add_steps(tc_infer)
    mgr.execute_steps()
    mgr.clear()
    assert True

