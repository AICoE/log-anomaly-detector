"""Validates if training was successful."""
import pytest

from anomaly_detector.adapters import SomModelAdapter, SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.core import SomTrainJob, SomInferenceJob
from anomaly_detector.storage.local_storage import DefaultStorageAttribute

NUM_LOG_LINES = 812


@pytest.mark.storage
@pytest.mark.localdir
def test_local_dir_ingest_retrieve(cnf_localdir):
    """Test anomaly detection training on public dataset."""
    storage_adapter = SomStorageAdapter(config=cnf_localdir, feedback_strategy=None)
    data, dataset = storage_adapter.storage.retrieve(DefaultStorageAttribute())
    print(len(data))
    assert len(data) == NUM_LOG_LINES


@pytest.mark.storage
@pytest.mark.localdir
def test_training_local_dir(cnf_localdir):
    """Test anomaly detection training on public dataset."""
    model_adapter = SomModelAdapter(SomStorageAdapter(config=cnf_localdir, feedback_strategy=None))
    tc_train = SomTrainJob(node_map=2, model_adapter=model_adapter, recreate_model=True)
    result, dist = tc_train.execute()
    assert result == 0
    model_adapter = SomModelAdapter(SomStorageAdapter(config=cnf_localdir, feedback_strategy=None))
    tc_infer = SomInferenceJob(model_adapter=model_adapter, sleep=False)
    result = tc_infer.execute()
    assert result == 0
