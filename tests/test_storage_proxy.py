"""Test storage proxy to validate if api rules are enforced."""
import pytest

from anomaly_detector.config import Configuration
from anomaly_detector.storage.storage_proxy import StorageProxy


@pytest.mark.storage
def test_storage_proxy_throws_exception(cnf_wrong_settings):
    """Test that if there is an invalid usage of api that we throw exception."""
    with pytest.raises(ValueError) as excinfo:
        StorageProxy(config=cnf_wrong_settings)
    assert excinfo.type == ValueError
