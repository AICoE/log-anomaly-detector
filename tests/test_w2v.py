"""Validates if training was successful."""
from anomaly_detector.adapters.som_model_adapter import SomModelAdapter
from anomaly_detector.adapters.som_storage_adapter import SomStorageAdapter
from anomaly_detector.core.job import SomTrainJob
import logging

import pytest

CONFIGURATION_PREFIX = "LAD"


@pytest.mark.core
@pytest.mark.w2v_model
def test_vocab_length(cnf_hadoop2k_w2v_params):
    """Check length of processed vocab on on Hadoop_2k.json."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop2k_w2v_params, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()

    assert len(model_adapter.w2v_model.model["message"].wv.vocab) == 141


@pytest.mark.core
@pytest.mark.w2v_model
def test_log_similarity(cnf_hadoop2k_w2v_params):
    """Check that two words have consistent similar logs after training."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop2k_w2v_params, feedback_strategy=None)
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
    logging.info(match_2[0])
    assert answer_2 in match_2


@pytest.mark.core
@pytest.mark.w2v_model
def test_loss_value(cnf_hadoop2k_w2v_params):
    """Check the loss value is not greater then during testing."""
    storage_adapter = SomStorageAdapter(config=cnf_hadoop2k_w2v_params, feedback_strategy=None)
    model_adapter = SomModelAdapter(storage_adapter=storage_adapter)
    tc = SomTrainJob(node_map=2, model_adapter=model_adapter)
    result, dist = tc.execute()
    logging.info(model_adapter.w2v_model.model["message"].get_latest_training_loss())
    tl = model_adapter.w2v_model.model["message"].get_latest_training_loss()
    assert tl < 320000.0
