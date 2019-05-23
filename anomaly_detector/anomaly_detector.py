"""Anomaly Detector main logic."""
import uuid
import datetime
import logging
import os
import time
import matplotlib
import numpy as np
from prometheus_client import start_http_server, Gauge, Counter
from .config import Configuration
from .events.anomaly_event import AnomalyEvent
from .model.model_exception import ModelLoadException, ModelSaveException
from .model.sompy_model import SOMPYModel
from .model.w2v_model import W2VModel
from .storage.es_storage import ESStorage
from .storage.local_storage import LocalStorage
from .exception.exceptions import factStoreEnvVarNotSetException
from requests.exceptions import ConnectionError

matplotlib.use("agg")

_LOGGER = logging.getLogger(__name__)

ANOMALY_THRESHOLD = Gauge("anomaly_threshold", "A threshold for anomaly")
TRAINING_COUNT = Counter("training_count", "Number of training runs")
TRAINING_TIME = Gauge("training_time", "Time to train for last training")
INFERENCE_COUNT = Counter("inference_count", "Number of inference runs")
PROCESSED_MESSAGES = Counter("inference_processed_count", "Number of log entries processed in inference")
ANOMALY_COUNT = Counter("anomaly_count", "Number of anomalies found")


class AnomalyDetector:
    """Implement training and inference of Self Organizing Map to detect anomalies in logs."""

    STORAGE_BACKENDS = [LocalStorage, ESStorage]

    def __init__(self, cfg: Configuration):
        """Initialize the anomaly detector."""
        self.config = cfg
        # model exists and update was requested
        self.update_model = os.path.isfile(cfg.MODEL_PATH) and cfg.TRAIN_UPDATE_MODEL
        self.update_w2v_model = os.path.isfile(cfg.W2V_MODEL_PATH) and cfg.TRAIN_UPDATE_MODEL
        self.recreate_models = False

        print("Threshold init: {}".format(self.config.INFER_ANOMALY_THRESHOLD))
        for backend in self.STORAGE_BACKENDS:
            if backend.NAME == self.config.STORAGE_BACKEND:
                _LOGGER.info("Using %s storage backend" % backend.NAME)
                self.storage = backend(cfg)
                break
        if not self.storage:
            raise Exception("Could not use %s storage backend" % self.STORAGE_BACKENDS)

        self.model = SOMPYModel()
        self.w2v_model = W2VModel()
        try:
            self.model.load(self.config.MODEL_PATH)
        except ModelLoadException as ex:
            _LOGGER.error("Failed to load SOM model: %s" % ex)
            self.update_model = False
            self.recreate_models = True

        try:
            self.w2v_model.load(self.config.W2V_MODEL_PATH)
        except ModelLoadException as ex:
            _LOGGER.error("Failed to load W2V model: %s" % ex)
            self.update_w2v_model = False
            self.recreate_models = True

    def _load_data(self, time_span, max_entries, fp=None):
        """Loading data from storage into pandas dataframe for processing."""
        data, raw = self.storage.retrieve(time_span, max_entries, fp)

        if len(data) == 0:
            _LOGGER.info("There are no logs in last %s seconds", time_span)
            return None, None

        return data, raw

    @TRAINING_TIME.time()
    # @profile
    def train(self, fp=None, node_map=24):
        """Train models for anomaly detection."""
        start = time.time()
        data, _ = self._load_data(self.config.TRAIN_TIME_SPAN, self.config.TRAIN_MAX_ENTRIES, fp)
        if data is None:
            return 1
        _LOGGER.info("Learning Word2Vec Models and Saving for Inference Step")
        then = time.time()
        if not self.recreate_models and self.update_w2v_model:
            self.w2v_model.update(data)
        else:
            self.w2v_model.create(data, self.config.TRAIN_VECTOR_LENGTH, self.config.TRAIN_WINDOW)
        try:
            self.w2v_model.save(self.config.W2V_MODEL_PATH)

        except ModelSaveException as ex:
            _LOGGER.error("Failed to save W2V model: %s" % ex)
            raise

        now = time.time()

        _LOGGER.info("Training and Saving took %s minutes", ((now - then) / 60))
        _LOGGER.info("Encoding Text Data")

        to_put_train = self.w2v_model.one_vector(data)
        _LOGGER.info("Start Training SOM...")

        dist = self.compute_score(node_map, to_put_train)

        self.model.set_metadata((np.mean(dist), np.std(dist), np.max(dist), np.min(dist)))
        try:
            self.model.save(self.config.MODEL_PATH)
        except ModelSaveException as ex:
            _LOGGER.error("Failed to save SOM model: %s" % ex)
            raise

        end = time.time()
        _LOGGER.info("Whole Process takes %s minutes", ((end - start) / 60))
        TRAINING_COUNT.inc()
        return 0, dist

    def compute_score(self, node_map, to_put_train):
        """Compute score for anomaly for SOM model."""
        then = time.time()
        if self.recreate_models or self.update_model:
            self.model.set(np.random.rand(node_map, node_map, to_put_train.shape[1]))
        self.model.train(to_put_train, node_map, self.config.TRAIN_ITERATIONS, self.config.PARALLELISM)
        now = time.time()
        dist = self.model.get_anomaly_score(to_put_train, self.config.PARALLELISM)
        _LOGGER.info("Training took %s minutes", ((now - then) / 60))
        _LOGGER.info("Generating Baseline Metrics")
        return dist

    def infer(self):
        """Perform inference on trained models."""
        meta_data = self.model.get_metadata()

        stdd = meta_data[1]
        mean = meta_data[0]
        threshold = self.config.INFER_ANOMALY_THRESHOLD * stdd + mean

        ANOMALY_THRESHOLD.set(threshold)
        _LOGGER.info("threshold for anomaly is of %f" % threshold)
        _LOGGER.info("Models loaded, running %d infer loops" % self.config.INFER_LOOPS)

        infer_loops = 0
        while infer_loops < self.config.INFER_LOOPS:
            INFERENCE_COUNT.inc()
            then = time.time()
            now = datetime.datetime.now()

            # Get data for inference
            data, json_logs = self._load_data(self.config.INFER_TIME_SPAN, self.config.INFER_MAX_ENTRIES)
            if data is None:
                time.sleep(5)
                continue

            _LOGGER.info("%d logs loaded from the last %d seconds", len(data), self.config.INFER_TIME_SPAN)

            try:
                self.w2v_model.update(data)
            except KeyError:
                _LOGGER.error("Word2Vec model fields incompatible")
                _LOGGER.error("Retrain model with log data")
                exit()

            v = self.w2v_model.one_vector(data)

            dist = []

            dist = self.model.get_anomaly_score(v, self.config.PARALLELISM)

            f = []

            _LOGGER.info("Max anomaly score: %f" % max(dist))
            for i in range(len(data)):
                _LOGGER.debug("Updating entry %d - dist: %f; mean: %f" % (i, dist[i], mean))

                # TODO: This needs to be more general,
                #       only works for ES incoming logs right now.
                s = json_logs[i]
                s["anomaly_score"] = dist[i]

                if dist[i] > threshold:
                    ANOMALY_COUNT.inc()
                    s["predict_id"] = str(uuid.uuid4())
                    try:
                        val = AnomalyEvent(
                            s["predict_id"], s["message"], dist[i], True, self.config.FACT_STORE_URL
                        ).is_event_false()
                        s["anomaly"] = val
                    except factStoreEnvVarNotSetException as f_ex:
                        _LOGGER.info("Fact Store Env Var is not set")
                        s["anomaly"] = 1
                    except ConnectionError as e:
                        _LOGGER.info("Fact store is down unable to check")
                        s["anomaly"] = 1
                    _LOGGER.warn("Anomaly found (score: %f): %s" % (dist[i], s["message"]))
                else:
                    s["anomaly"] = 0
                f.append(s)
            PROCESSED_MESSAGES.inc(len(f))
            self.storage.store_results(f)
            # Inference done, increase counter
            infer_loops += 1
            now = time.time()
            _LOGGER.info("Analyzed one minute of data in %s seconds", (now - then))
            _LOGGER.info("waiting for next minute to start...")
            _LOGGER.info("press ctrl+c to stop process")
            sleep_time = self.config.INFER_TIME_SPAN - (now - then)
            if sleep_time > 0:
                time.sleep(sleep_time)

        # When we reached # of inference loops, retrain models
        self.recreate_models = False

    def run(self, single_run=False):
        """Run the main loop."""
        start_http_server(8080)
        srun = False
        fp = None
        while True and srun is False:
            if self.update_model or self.update_w2v_model or self.recreate_models:
                try:
                    self.train(fp=fp)
                except Exception as ex:
                    _LOGGER.error("Training failed: %s" % ex)
                    raise
            else:
                _LOGGER.info("Models already exists, skipping training")
            try:
                self.infer()
            except Exception as ex:
                _LOGGER.error("Inference failed: %s" % ex)
                raise ex
            srun = single_run
