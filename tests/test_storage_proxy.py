"""Test storage proxy to validate if api rules are enforced."""
import pytest

from anomaly_detector.config import Configuration
from anomaly_detector.storage.storage_proxy import StorageProxy


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration()
    config.STORAGE_DATASOURC = "local.source"
    config.STORAGE_DATASINK = "local.sink"
    config.LS_INPUT_PATH = "validation_data/orders-500.log"
    config.LS_OUTPUT_PATH = "validation_data/results-oct4.1.txt"
    return config


def test_storage_proxy_throws_exception(config):
    """Test that if there is an invalid usage of api that we throw exception."""
    with pytest.raises(ValueError) as excinfo:
        StorageProxy(config=config)
    assert excinfo.type == ValueError
