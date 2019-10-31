"""Validates if training was successful."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.core.job import SomTrainJob, SomInferenceJob
from anomaly_detector.config import Configuration

import pytest

CONFIGURATION_PREFIX = "LAD"


@pytest.fixture()
def config():
    """Initialize configurations before testing."""
    config = Configuration()
    config.STORAGE_DATASOURCE = "local"
    config.STORAGE_DATASINK = "stdout"
    config.LS_INPUT_PATH = "validation_data/Hadoop_2k.json"
    config.W2V_MIN_COUNT = 1
    config.W2V_ITER = 500
    config.W2V_COMPUTE_LOSS = "True"
    config.W2V_SEED = 50
    config.W2V_WORKERS = 1
    return config


def test_vocab_length(config):
    """Check length of processed vocab on on Hadoop_2k.json."""
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()

    assert len(model_adapter.w2v_model.model["message"].wv.vocab) == 141


def test_log_similarity(config):
    """Check that two words have consistent similar logs after training."""
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    log_1 = 'INFOmainorgapachehadoopmapreducevappMRAppMasterExecutingwithtokens'
    answer_1 = 'INFOmainorgapachehadoopmapreducevappMRAppMasterCreatedMRAppMasterforapplicationappattempt'

    match_1 = [model_adapter.w2v_model.model["message"].wv.most_similar(log_1)[i][0] for i in range(3)]
    assert answer_1 in match_1

    log_2 = 'ERRORRMCommunicatorAllocatororgapachehadoopmapreducevapprmRMContainerAllocatorERRORINCONTACTINGRM'
    answer_2 = 'WARNLeaseRenewermsrabimsrasaorgapachehadoophdfsLeaseRenewerFailedtorenewleaseforDFSClient' \
               'NONMAPREDUCEforsecondsWillretryshortly'
    match_2 = [model_adapter.w2v_model.model["message"].wv.most_similar(log_2)[i][0] for i in range(3)]
    print(match_2[0])
    assert answer_2 in match_2


def test_loss_value(config):
    """Check the loss value is not greater then during testing."""
    storage_adapter = SomStorageAdapter(config=config, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    print(model_adapter.w2v_model.model["message"].get_latest_training_loss())
    tl = model_adapter.w2v_model.model["message"].get_latest_training_loss()
    assert tl < 320000.0
