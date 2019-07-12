"""Som Model Adapter - Working with custom implementation of SOM."""
import logging
import uuid
import numpy as np
from anomaly_detector.adapters.base_model_adapter import BaseModelAdapter
from anomaly_detector.decorator.utils import latency_logger
from anomaly_detector.events.anomaly_event import AnomalyEvent
from anomaly_detector.exception.exceptions import factStoreEnvVarNotSetException
from anomaly_detector.model.model_exception import ModelLoadException, ModelSaveException
from anomaly_detector.model.sompy_model import SOMPYModel
from anomaly_detector.model.w2v_model import W2VModel
import os
from prometheus_client import Gauge, Summary, Counter, Histogram

ANOMALY_COUNT = Gauge("aiops_lad_anomaly_count", "count of anomalies runs", ['anomaly_status'])
ANOMALY_SCORE = Gauge("aiops_lad_anomaly_avg_score", "avg anomaly score")
LOG_LINES_COUNT = Gauge("aiops_lad_loglines_count", "count of log lines processed runs")
FALSE_POSITIVE_COUNT = Counter("aiops_lad_false_positive_count", "count of false positives processed runs", ['id'])
ANOMALY_HIST = Histogram("aiops_hist", "histogram of anomalies runs")
THRESHOLD = Gauge("aiops_lad_threshold", "Threshold of marker for anomaly")


class SomModelAdapter(BaseModelAdapter):
    """Self organizing map custom logic to train model. Includes logic to train and predict anomalies in logs."""

    def __init__(self, storage_adapter):
        """Init storage provider which provides config and storage interface with storage systems."""
        self.storage_adapter = storage_adapter
        update_model = self.storage_adapter.TRAIN_UPDATE_MODEL
        self.update_model = os.path.isfile(self.storage_adapter.MODEL_PATH) and update_model
        self.update_w2v_model = os.path.isfile(self.storage_adapter.W2V_MODEL_PATH) and update_model
        self.recreate_models = False
        self.model = SOMPYModel()
        self.w2v_model = W2VModel()

    def load_w2v_model(self):
        """Load in w2v model."""
        try:
            self.w2v_model.load(self.storage_adapter.W2V_MODEL_PATH)
        except ModelLoadException as ex:
            logging.error("Failed to load W2V model: %s" % ex)
            raise

    def load_som_model(self):
        """Load in w2v model."""
        try:
            self.model.load(self.storage_adapter.MODEL_PATH)
        except ModelLoadException as ex:
            logging.error("Failed to load SOM model: %s" % ex)
            raise

    @latency_logger(name="SomModelAdapter")
    def train(self, node_map, data, recreate_model=True):
        """Train som model after creating vectors from words using w2v model."""
        to_put_train = self.w2v_model.one_vector(data)
        # If node_map is none then we assume it is calculating score for inference
        if recreate_model is True:
            self.model.set(np.random.rand(node_map, node_map, to_put_train.shape[1]))
        self.model.train(to_put_train, node_map, self.storage_adapter.TRAIN_ITERATIONS,
                         self.storage_adapter.PARALLELISM)
        dist = self.model.get_anomaly_score(to_put_train, self.storage_adapter.PARALLELISM)
        self.model.set_metadata((np.mean(dist), np.std(dist), np.max(dist), np.min(dist)))
        try:
            self.model.save(self.storage_adapter.MODEL_PATH)
        except ModelSaveException as ex:
            logging.error("Failed to save SOM model: %s" % ex)
            raise
        return dist

    @latency_logger(name="SomModelAdapter")
    def preprocess(self, config_type, recreate_model):
        """Load data and train."""
        data, raw = self.storage_adapter.load_data(config_type)
        # if data:
        if data is not None:
            LOG_LINES_COUNT.set(len(data))
            if not recreate_model:
                self.w2v_model.update(data)
            else:
                self.w2v_model.create(data, self.storage_adapter.TRAIN_VECTOR_LENGTH, self.storage_adapter.TRAIN_WINDOW)
            try:
                self.w2v_model.save(self.storage_adapter.W2V_MODEL_PATH)
            except ModelSaveException as ex:
                logging.error("Failed to save W2V model: %s" % ex)
                raise

        return data, raw

    @latency_logger(name="SomModelAdapter")
    def predict(self, data, json_logs, threshold):
        """Prediction from data provided and if it hits threshold it flags it an anomaly."""
        feedback_strategy = self.storage_adapter.feedback_strategy
        false_positives = feedback_strategy.execute() if feedback_strategy else None
        dist = self.process_anomaly_score(data)
        f = []
        hist_count = 0
        logging.info("Max anomaly score: %f" % max(dist))
        for i in range(len(data)):
            s = json_logs[i]
            s["predict_id"] = str(uuid.uuid4())
            s["anomaly_score"] = dist[i]
            # Record anomaly event in fact_store and
            if false_positives is not None:
                if {"message": s["message"]} in false_positives:
                    logging.info("False positive was found (score: %f): %s" % (dist[i], s["message"]))
                    FALSE_POSITIVE_COUNT.labels(id=s["predict_id"]).inc()
                    continue
            if dist[i] > threshold:
                hist_count += 1
                s["anomaly"] = 1
                logging.warning("Anomaly found (score: %f): %s" % (dist[i], s["message"]))
                ANOMALY_SCORE.set(dist[i])
            else:
                s["anomaly"] = 0
            # anomaly_status==1 means its an anomaly otherwise its not we may want to do some comparison.
            ANOMALY_COUNT.labels(anomaly_status=s["anomaly"]).inc()

            if self.storage_adapter.FACT_STORE_URL is not "":
                self.process_false_positives(data, dist, i, s)
            ANOMALY_HIST.observe(hist_count)
            f.append(s)
        return f

    def process_false_positives(self, data, dist, i, s):
        """Process false positive data in feedback store."""
        try:
            logging.info("Progress of anomaly events record {} of {} ".format(i, len(data)))

            AnomalyEvent(
                s["predict_id"], s["message"], dist[i], s["anomaly"], self.storage_adapter.FACT_STORE_URL
            ).record_prediction()
        except factStoreEnvVarNotSetException as f_ex:
            logging.info("Fact Store Env Var is not set")

        except ConnectionError as e:
            logging.info("Fact store is down unable to check")

    @latency_logger(name="SomModelAdapter")
    def process_anomaly_score(self, data):
        """Generate scores from some. To be used for inference."""
        v = self.w2v_model.one_vector(data)
        dist = []
        dist = self.model.get_anomaly_score(v, self.storage_adapter.PARALLELISM)
        return dist

    def set_threshold(self):
        """Setting threshold for prediction."""
        meta_data = self.model.get_metadata()
        stdd = meta_data[1]
        mean = meta_data[0]
        threshold = self.storage_adapter.INFER_ANOMALY_THRESHOLD * stdd + mean
        THRESHOLD.set(threshold)
        logging.info("threshold for anomaly is of %f" % threshold)
        logging.info("Models loaded, running %d infer loops" % self.storage_adapter.INFER_LOOPS)
        return mean, threshold
