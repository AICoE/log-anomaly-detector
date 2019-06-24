"""Validate input test cases to validate exception is thrown."""
import pytest
from anomaly_detector.config import Configuration
from anomaly_detector.exception.exceptions import EmptyDataSetNotAllowed
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
import pandas

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration(config_yaml=".env_config.yaml")
    return config


def test_empty_dataset(config):
    """Test empty dataframe and validate that it throws exception if so."""
    with pytest.raises(EmptyDataSetNotAllowed):
        storage = SomStorageAdapter(config)
        som = SomModelAdapter(storage_adapter=storage)
        som.process_anomaly_score(pandas.DataFrame())
