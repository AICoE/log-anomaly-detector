"""Som Model Adapter - Working with custom implementation of SOM."""
import logging
import uuid
import numpy as np
from anomaly_detector.adapters import BaseModelAdapter
from anomaly_detector.decorator.utils import latency_logger
from anomaly_detector.exception import ModelLoadException, ModelSaveException
from anomaly_detector.model import SOMPYModel, W2VModel
import os
from prometheus_client import Gauge, Counter, Histogram
from urllib.parse import quote

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
        self.model = SOMPYModel(config=storage_adapter.config)
        self.w2v_model = W2VModel(config=storage_adapter.config)

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
        vectors = self.w2v_model.one_vector(data)
        # If node_map is none then we assume it is calculating score for inference
        if recreate_model is True:
            self.model.set(np.random.rand(node_map, node_map, vectors.shape[1]))
        self.model.train(vectors, node_map, self.storage_adapter.TRAIN_ITERATIONS,
                         self.storage_adapter.PARALLELISM)
        dist = self.model.get_anomaly_score(vectors, self.storage_adapter.PARALLELISM)
        max_dist = np.max(dist)
        dist = dist / max_dist
        self.model.set_metadata((np.mean(dist), np.std(dist), max_dist, np.min(dist)))
        try:
            self.model.save(self.storage_adapter.MODEL_PATH)
        except ModelSaveException as ex:
            logging.error("Failed to save SOM model: %s" % ex)
            raise
        return dist

    @latency_logger(name="SomModelAdapter")
    def preprocess(self, config_type, recreate_model):
        """Load data and train."""
        dataframe, raw_data = self.storage_adapter.load_data(config_type)
        if dataframe is not None:
            LOG_LINES_COUNT.set(len(dataframe))
            if not recreate_model:
                self.w2v_model.update(dataframe)
            else:
                self.w2v_model.create(dataframe,
                                      self.storage_adapter.TRAIN_VECTOR_LENGTH,
                                      self.storage_adapter.TRAIN_WINDOW)
            try:
                self.w2v_model.save(self.storage_adapter.W2V_MODEL_PATH)
            except ModelSaveException as ex:
                logging.error("Failed to save W2V model: %s" % ex)
                raise

        return dataframe, raw_data

    @latency_logger(name="SomModelAdapter")
    def predict(self, data, json_logs, threshold):
        """Prediction from data provided and if it hits threshold it flags it an anomaly."""
        feedback_strategy = self.storage_adapter.feedback_strategy
        inference_batch_id = str(uuid.uuid4())
        false_positives = None
        if feedback_strategy is not None:
            false_positives = feedback_strategy.execute()
        logging.info("False Positive: {} ".format(false_positives))
        dist = self.process_anomaly_score(data)
        f = []
        hist_count = 0
        logging.info("Max anomaly score: %f" % max(dist))
        ANOMALY_COUNT._metrics.clear()

        last_id = dict()
        for i in range(len(data)):
            s = json_logs[i]
            s["predict_id"] = str(uuid.uuid4())
            s["anomaly_score"] = dist[i]
            s["elast_alert"] = self.storage_adapter.ES_ELAST_ALERT
            s["inference_batch_id"] = inference_batch_id
            s["predictor_namespace"] = self.storage_adapter.OS_NAMESPACE
            s["e_message"] = quote(s["message"])
            # Record anomaly event in fact_store
            if dist[i] > threshold:
                if false_positives is not None:
                    if s["message"] in feedback_strategy.uniq_items:
                        # logging.info("False positive was found (score: %f): %s" % (dist[i], s["message"]))
                        FALSE_POSITIVE_COUNT.labels(id=s["predict_id"]).inc()
                        continue
                hist_count += 1
                s["anomaly"] = 1
                logging.warning("Anomaly found (score: %f): %s" % (dist[i], s["message"]))
                last_id[quote(s["message"])] = s["predict_id"]
                ANOMALY_SCORE.set(dist[i])
            else:
                s["anomaly"] = 0
            ANOMALY_COUNT.labels(anomaly_status=s["anomaly"]).inc()
            ANOMALY_HIST.observe(hist_count)
            f.append(s)
        return f

    @latency_logger(name="SomModelAdapter")
    def process_anomaly_score(self, data):
        """Generate scores from some. To be used for inference."""
        meta_data = self.model.get_metadata()
        max_dist = meta_data[2]
        v = self.w2v_model.one_vector(data)
        dist = []
        dist = self.model.get_anomaly_score(v, self.storage_adapter.PARALLELISM)
        dist = dist / max_dist
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
