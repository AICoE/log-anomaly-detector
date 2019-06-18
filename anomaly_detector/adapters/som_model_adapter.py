"""Som Model Adapter - Working with custom implementation of SOM."""
import datetime
import logging
import os
import time
import uuid

import numpy as np

from anomaly_detector.adapters.base_model_adapter import BaseModelAdapter
from anomaly_detector.events.anomaly_event import AnomalyEvent
from anomaly_detector.exception.exceptions import factStoreEnvVarNotSetException
from anomaly_detector.model.model_exception import ModelLoadException, ModelSaveException
from anomaly_detector.model.sompy_model import SOMPYModel
from anomaly_detector.model.w2v_model import W2VModel


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
        try:
            self.model.load(self.storage_adapter.MODEL_PATH)
        except ModelLoadException as ex:
            logging.error("Failed to load SOM model: %s" % ex)
            self.update_model = False
            self.recreate_models = True
        try:
            self.w2v_model.load(self.storage_adapter.W2V_MODEL_PATH)
        except ModelLoadException as ex:
            logging.error("Failed to load W2V model: %s" % ex)
            self.update_w2v_model = False
            self.recreate_models = True

    def run(self, single_run=False):
        """Run the main loop."""
        break_out = False
        while break_out is False:
            if self.update_model or self.update_w2v_model or self.recreate_models:
                try:
                    self.train()
                except Exception as ex:
                    logging.error("Training failed: %s" % ex)
                    raise
            else:
                logging.info("Models already exists, skipping training")
            try:
                self.infer()
            except Exception as ex:
                logging.error("Inference failed: %s" % ex)
                raise ex
            break_out = single_run

    def train(self, node_map=24):
        """Train models for anomaly detection."""
        data, _ = self.storage_adapter.load_data(config_type="train")
        then = time.time()
        self.prepare_w2v_model(data)
        now = time.time()
        logging.info("Training and Saving took %s minutes", ((now - then) / 60))
        dist = self.compute_score(node_map, data)
        self.model.set_metadata((np.mean(dist), np.std(dist), np.max(dist), np.min(dist)))
        try:
            self.model.save(self.storage_adapter.MODEL_PATH)
        except ModelSaveException as ex:
            logging.error("Failed to save SOM model: %s" % ex)
            raise
        end = time.time()
        logging.info("Whole Process takes %s minutes", ((end - then) / 60))
        return 0, dist

    def prepare_w2v_model(self, data):
        """w2v needs to be updated with new data as it turns log lines into vector representation for SOM."""
        if not self.recreate_models and self.update_w2v_model:
            self.w2v_model.update(data)
        else:
            self.w2v_model.create(data, self.storage_adapter.TRAIN_VECTOR_LENGTH, self.storage_adapter.TRAIN_WINDOW)
        try:
            self.w2v_model.save(self.storage_adapter.W2V_MODEL_PATH)
        except ModelSaveException as ex:
            logging.error("Failed to save W2V model: %s" % ex)
            raise

    def compute_score(self, node_map=None, data=None):
        """Compute score for anomaly for SOM model."""
        to_put_train = self.w2v_model.one_vector(data)
        # If node_map is none then we assume it is calculating score for inference
        then = time.time()
        if self.recreate_models or self.update_model:
            self.model.set(np.random.rand(node_map, node_map, to_put_train.shape[1]))
        self.model.train(to_put_train, node_map, self.storage_adapter.TRAIN_ITERATIONS,
                         self.storage_adapter.PARALLELISM)
        now = time.time()
        logging.info("Training took %s minutes", ((now - then) / 60))
        dist = self.model.get_anomaly_score(to_put_train, self.storage_adapter.PARALLELISM)
        return dist

    def infer(self):
        """Perform inference on trained models."""
        mean, threshold = self.set_threshold()

        infer_loops = 0
        while infer_loops < self.storage_adapter.INFER_LOOPS:
            then = time.time()
            now = datetime.datetime.now()
            # Get data for inference
            data, json_logs = self.storage_adapter.load_data(config_type="infer")
            if data is None:
                time.sleep(5)
                continue
            logging.info("%d logs loaded from the last %d seconds", len(data), self.storage_adapter.INFER_TIME_SPAN)
            try:
                self.w2v_model.update(data)
            except KeyError:
                logging.error("Word2Vec model fields incompatible")
                logging.error("Retrain model with log data")
                exit()
            f = self.prediction_builder(data, json_logs, threshold)
            self.storage_adapter.persist_data(f)
            # Inference done, increase counter
            infer_loops += 1
            now = time.time()
            logging.info("Analyzed one minute of data in %s seconds", (now - then))
            logging.info("waiting for next minute to start...")
            logging.info("press ctrl+c to stop process")
            sleep_time = self.storage_adapter.INFER_TIME_SPAN - (now - then)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # When we reached # of inference loops, retrain models
        self.recreate_models = False
        return 0

    def prediction_builder(self, data, json_logs, threshold):
        """Prediction from data provided and if it hits threshold it flags it an anomaly."""
        false_positives = self.storage_adapter.feedback_strategy.execute()
        dist = self.process_anomaly_score(data)
        f = []
        logging.info("Max anomaly score: %f" % max(dist))
        for i in range(len(data)):
            s = json_logs[i]
            s["predict_id"] = str(uuid.uuid4())
            s["anomaly_score"] = dist[i]
            # Record anomaly event in fact_store and
            if false_positives is not None:
                if {"message": s["message"]} in false_positives:
                    logging.info("False positive was found (score: %f): %s" % (dist[i], s["message"]))
                    continue
            if dist[i] > threshold:
                s["anomaly"] = 1
                logging.warning("Anomaly found (score: %f): %s" % (dist[i], s["message"]))

            else:
                s["anomaly"] = 0
            try:
                logging.info("Progress of anomaly events record {} of {} ".format(i, len(data)))

                AnomalyEvent(
                    s["predict_id"], s["message"], dist[i], s["anomaly"], self.storage_adapter.FACT_STORE_URL
                ).record_prediction()
            except factStoreEnvVarNotSetException as f_ex:
                logging.info("Fact Store Env Var is not set")

            except ConnectionError as e:
                logging.info("Fact store is down unable to check")
            f.append(s)
        return f

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
        logging.info("threshold for anomaly is of %f" % threshold)
        logging.info("Models loaded, running %d infer loops" % self.storage_adapter.INFER_LOOPS)
        return mean, threshold
