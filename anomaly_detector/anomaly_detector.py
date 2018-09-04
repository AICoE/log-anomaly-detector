from elasticsearch2 import Elasticsearch, helpers
from gensim.models import Word2Vec
import json
import os, sys
import numpy as np
from pandas.io.json import json_normalize
from sklearn.externals import joblib
from scipy.spatial.distance import cosine
import datetime
import logging
import re
import time
import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt
import warnings
from tqdm import tqdm

from .storage.es_storage import ESStorage
from .storage.local_storage import LocalStorage
from .config import Configuration
from .model.som_model import SOMModel
from .model.model_exception import ModelLoadException, ModelSaveException
from .model.w2v_model import W2VModel

logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO)

class AnomalyDetector():
  STORAGE_BACKENDS = [LocalStorage, ESStorage]

  def __init__(self, configuration: Configuration):   
    self.config = configuration
    self.update_model = os.path.isfile(configuration.MODEL_PATH) and configuration.TRAIN_UPDATE_MODEL #model exists and update was requested
    self.update_w2v_model = os.path.isfile(configuration.W2V_MODEL_PATH) and configuration.TRAIN_UPDATE_MODEL #model exists and update was requested
    self.model_load_failed = False

    for backend in self.STORAGE_BACKENDS:
      if backend.NAME == self.config.STORAGE_BACKEND:
        logging.info("Using %s storage backend" % backend.NAME)
        self.storage = backend(configuration)
        break
    if not self.storage:
      raise Exception("Could not use %s storage backend" % self.STORAGE_BACKENDS)

    self.model = SOMModel()
    self.w2v_model = W2VModel()
    try:
      self.model.load(self.config.MODEL_PATH)
    except ModelLoadException as ex:
      logging.error("Failed to load SOM model: %s" % ex)
      self.update_model = False
      self.model_load_failed = True

    try:
      self.w2v_model.load(self.config.W2V_MODEL_PATH)
    except ModelLoadException as ex:
      logging.error("Failed to load W2V model: %s" % ex)
      self.update_w2v_model = False
      self.model_load_failed = True

  def _load_data(self, time_span, max_entries):
    data, raw = self.storage.retrieve(time_span, max_entries)
      
    if len(data) == 0:
        logging.info("There are no logs for this service in the last %s seconds", time_span)
        return None, None

    return data, raw

  def train(self):
      T_Then = time.time()
      warnings.filterwarnings("ignore")

      #Get data for training
      data, _ = self._load_data(self.config.TRAIN_TIME_SPAN, self.config.TRAIN_MAX_ENTRIES)
      if data is None:
        return 1
      
      logging.info("Learning Word2Vec Models and Saving for Inference Step")

      then = time.time()

      if self.update_w2v_model:
        new_D, models = self.w2v_model.update(data)
      else:
        new_D, models = self.w2v_model.create(data)
      
      try:
        self.w2v_model.save(self.config.W2V_MODEL_PATH)
      except ModelSaveException as ex:
        logging.error("Failed to save W2V model: %s" % ex)
        raise

      now = time.time()

      logging.info("Training and Saving took %s minutes",((now-then)/60))
      logging.info("Encoding Text Data")

      to_put_train = self.w2v_model.one_vector(new_D)
      
      logging.info("Start Training SOM...")
      
      then = time.time()

      if not self.model or self.update_model:
          self.model.set(np.random.rand(24, 24, to_put_train.shape[1]))

      self.model.train(to_put_train, 24, self.config.TRAIN_ITERATIONS)
      now = time.time()

      logging.info("Training took %s minutes",((now-then)/60)) 
      logging.info('Saving U-map')
      self.model.save_visualisation(self.config.MODEL_DIR)
      logging.info("Generating Baseline Metrics")

      dist = []
      for i in tqdm(to_put_train):
          dist.append(self.model.get_anomaly_score(i))

      self.model.set_metadata((np.mean(dist), np.std(dist), np.max(dist),np.min(dist)))
      try:
        self.model.save(self.config.MODEL_PATH)
      except ModelSaveException as ex:
        logging.error("Failed to save SOM model: %s" % ex)
        raise

      T_Now = time.time()
      logging.info("Whole Process takes %s minutes", ((T_Now-T_Then)/60))

      return 0

  def infer(self):
    w2v_model_stored = self.w2v_model.load(self.config.W2V_MODEL_PATH)

    som_model = self.model.get()
    meta_data = self.model.get_metadata()
    maxx = meta_data[2]
    stdd = meta_data[1]

    logging.info("Maxx: %f, stdd: %f" % (maxx, stdd))

    logging.info("Models loaded, running %d infer loops" % self.config.INFER_LOOPS)

    for i in range(self.config.INFER_LOOPS):
      then = time.time()
      now = datetime.datetime.now()

      #Get data for inference
      data, json_logs = self._load_data(self.config.INFER_TIME_SPAN, self.config.INFER_MAX_ENTRIES)
      if data is None:
        time.sleep(5)
        continue
      
      logging.info("%d logs loaded from the last %d seconds", len(data) , self.config.INFER_TIME_SPAN)

      try:
        new_D, _ = self.w2v_model.update(data)
      except KeyError:
        logging.error("Word2Vec model fields incompatible with current log set. Retrain model with log data from the same service")
        exit()
      
      v = self.w2v_model.one_vector(new_D)

      dist = []
      for i in v:
        dist.append(self.model.get_anomaly_score(i))
      
      f = []

      logging.info("Max anomaly score: %f" % max(dist))
      for i in range(len(data)):
        logging.debug("Updating entry %d - dist: %f; maxx: %f" % (i, dist[i], maxx))
        s = json_logs[i]  # This needs to be more general, only works for ES incoming logs right now. 
        s['anomaly_score'] = dist[i] 

        if dist[i] > (self.config.INFER_ANOMALY_THRESHOLD * maxx):
          s['anomaly'] = 1
          logging.warn("Anomaly found (score: %f): %s" % (dist[i], s['message']))
        else:
          s['anomaly'] = 0

        f.append(s)
          
      self.storage.store_results(f)

      now = time.time()
      logging.info("Analyzed one minute of data in %s seconds",(now-then))
      logging.info("waiting for next minute to start...") 
      logging.info("press ctrl+c to stop process")
      sleep_time = self.config.INFER_TIME_SPAN-(now-then)
      if sleep_time > 0:
        time.sleep(sleep_time)

  def run(self):
    while True:
      if not os.path.isfile(self.config.MODEL_PATH) or self.config.TRAIN_UPDATE_MODEL or\
           self.model_load_failed:
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
        raise
        time.sleep(5)