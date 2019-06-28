"""Test case for validating task manager."""
from unittest import TestCase
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.config import Configuration
from anomaly_detector.jobs.tasks import *

TASKS_IN_QUEUE = 1


class TestTaskManager(TestCase):
    """Task Manager test case to validate the commands we run in system."""

    def test_train_command(self):
        """Test case for validating that when we train a model and add it to task queue that it will run."""
        mgr = TaskQueue()
        config = Configuration(config_yaml=".env_config.yaml")
        storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
        model_adapter = SomModelAdapter(storage_adapter)
        tc = SomTrainCommand(node_map=2, model_adapter=model_adapter)

        mgr.add_steps(tc)
        self.assertEqual(len(mgr), TASKS_IN_QUEUE)
        self.assertNotEqual(mgr.count, TASKS_IN_QUEUE)
        mgr.execute_steps()
        self.assertEqual(mgr.count, TASKS_IN_QUEUE)

    def test_invalid_command(self):
        """Test case for validating that when we train a model and add it to task queue that it will run."""
        mgr = TaskQueue()

        class mock_func:
            def execute(self):
                print("Test")

        mock = mock_func()
        with self.assertRaises(TypeError) as context:
            mgr.add_steps(mock)

    def test_valid_command(self):
        """Test case for validating that when we train a model and add it to task queue that it will run."""
        mgr = TaskQueue()

        class mock_func(AbstractCommand):
            def execute(self):
                print("Test")

        mock = mock_func()
        mgr.add_steps(mock)
        self.assertEqual(len(mgr), TASKS_IN_QUEUE)
        self.assertNotEqual(mgr.count, TASKS_IN_QUEUE)
        mgr.execute_steps()
        self.assertEqual(mgr.count, TASKS_IN_QUEUE)
