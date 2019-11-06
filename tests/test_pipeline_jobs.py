"""Test case for testing pipeline."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.core import SomTrainJob, AbstractCommand
import pytest
import logging

TASKS_IN_QUEUE = 1


@pytest.mark.core
@pytest.mark.pipeline
def test_train_command(cnf_hadoop_2k, pipeline):
    """Test case for validating that when we train a model and add it to task queue that it will run."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop_2k, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter)
    train_job = SomTrainJob(node_map=2, model_adapter=model_adapter)
    pipeline.add_steps(train_job)
    assert len(pipeline) == TASKS_IN_QUEUE
    assert pipeline.count != TASKS_IN_QUEUE
    pipeline.execute_steps()
    assert pipeline.count == TASKS_IN_QUEUE


@pytest.mark.core
@pytest.mark.pipeline
def test_invalid_command(pipeline):
    """Throw exception if job does not extend AbstractCommand."""
    class mock_func:
        def execute(self):
            logging.info("Test")

    mock = mock_func()
    with pytest.raises(TypeError):
        pipeline.add_steps(mock)


@pytest.mark.core
@pytest.mark.pipeline
def test_valid_command(pipeline):
    """Run job successfuly as mock function extends AbstractCommand."""
    class mock_func(AbstractCommand):
        def execute(self):
            logging.info("Test")

    mock = mock_func()
    pipeline.add_steps(mock)
    assert len(pipeline) == TASKS_IN_QUEUE
    assert pipeline.count != TASKS_IN_QUEUE
    pipeline.execute_steps()
    assert pipeline.count == TASKS_IN_QUEUE
