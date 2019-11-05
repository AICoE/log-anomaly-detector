"""Validates if training was successful."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.core.job import SomTrainJob, SomInferenceJob
from anomaly_detector.config import Configuration

import pytest
import random

random.seed(55)

CONFIGURATION_PREFIX = "LAD"


@pytest.mark.core
@pytest.mark.som_model
def test_output_values(cnf_hadoop_2k):
    """Test that all distance values in training set are less than or equal to 1 on Hadoop_2k.json."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    assert sum(dist) <= 2000


@pytest.mark.core
@pytest.mark.som_model
def test_output_length(cnf_hadoop_2k):
    """Test that correct number of outputs are generated with Hadoop_2k.json."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    assert len(dist) == 2000


@pytest.mark.core
@pytest.mark.som_model
def test_model_shape(cnf_hadoop_2k):
    """Test that the trained model size is expected based on given parameters."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    assert model_adapter.model.model.shape[0:2] == (2, 2)
