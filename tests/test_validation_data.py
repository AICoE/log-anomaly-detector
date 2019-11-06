"""Validates if training was successful."""
import pytest
from anomaly_detector.adapters import SomModelAdapter, SomStorageAdapter
from anomaly_detector.core import SomTrainJob, SomInferenceJob
from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"


@pytest.mark.core
@pytest.mark.pipeline
def test_end2endtraining(cnf_hadoop_2k):
    """Test anomaly detection training on public dataset."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    assert result == 0


@pytest.mark.core
@pytest.mark.pipeline
def test_training_infer(cnf_hadoop_2k):
    """Test anomaly detection training on public dataset."""
    model_adapter = SomModelAdapter(SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None))
    tc_train = SomTrainJob(node_map=2, model_adapter=model_adapter, recreate_model=True)
    result, dist = tc_train.execute()
    assert result == 0
    model_adapter = SomModelAdapter(SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None))
    tc_infer = SomInferenceJob(model_adapter=model_adapter, sleep=False)
    result = tc_infer.execute()
    assert result == 0
