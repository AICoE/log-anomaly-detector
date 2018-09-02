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

from . import utils
from .SOM import SOM
from .storage.es_storage import ESStorage
from .storage.local_storage import LocalStorage
from .config import Configuration

logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO)

class AnomalyDetector():
  STORAGE_BACKENDS = [LocalStorage, ESStorage]

  def __init__(self, configuration: Configuration):   
    self.config = configuration
    self.update = os.path.isfile(configuration.MODEL_PATH) and configuration.TRAIN_UPDATE_MODEL #model exists and update was requested

    for backend in self.STORAGE_BACKENDS:
      if backend.NAME == self.config.STORAGE_BACKEND:
        logging.info("Using %s storage backend" % backend.NAME)
        self.storage = backend(configuration)
        break
    if not self.storage:
      raise Exception("Could not use %s storage backend" % self.STORAGE_BACKENDS)

  def train(self):
      T_Then = time.time()
      warnings.filterwarnings("ignore")
      print(self.config.MODEL_PATH)
      if self.update:
          m = utils.load_map(self.config.MODEL_PATH)
          m = m[0]
          w2v_model_stored = utils.load_map(self.config.W2V_MODEL_PATH)
      else:
          m = 0

      #Get data for training
      data, _ = self.storage.retrieve(self.config.TRAIN_TIME_SPAN, self.config.TRAIN_MAX_ENTRIES)
      
      if len(data) == 0:
          logging.info("There are no logs for this service in the last %s seconds", self.config.TRAIN_TIME_SPAN)
          logging.info("Waiting 60 seconds and trying again")
          time.sleep(60)
          return 1

      logging.info("Preprocessing logs & cleaning messages")

      for lines in range(len(data)):
          data["_source.message"][lines] = utils.clean_message(data["_source.message"][lines]) 

      # Below code for user feedback    
      # if os.path.isfile("found_anomalies.csv") == True:

      #     f = pd.read_csv("found_anomalies.csv")
      #     extra = f[f["label"] == 0]
      #     extra = extra.drop("label", axis=1)
      #     extra = extra.drop("Unnamed: 0", axis = 1)
      #     new_D.append(extra)
      
      logging.info("Learning Word2Vec Models and Saving for Inference Step")

      then = time.time()

      if self.update:
          models = w2v_model_stored
          try:
              new_D, models = utils.update_w2v_models(w2v_model_stored, data)
          except KeyError:
              logging.error("Can't update current Word2Vec model. Log fileds incompatible")
              exit()
          joblib.dump(models, self.config.W2V_MODEL_PATH)
      else:
        models, new_D = utils.make_models(data, True, self.config.W2V_MODEL_PATH)

      now = time.time()

      logging.info("Training and Saving took %s minutes",((now-then)/60))
      logging.info("Encoding Text Data")

      transforms = utils.transform_text(models,new_D)
      to_put_train = utils.one_vector(transforms)
      
      logging.info("Start Training SOM...")
      
      then = time.time()

      if not self.update:
          m = np.random.rand(24,24,to_put_train.shape[1])
      
      som_model = SOM(to_put_train,24, self.config.TRAIN_ITERATIONS, m)
      now = time.time()

      logging.info("Training took %s minutes",((now-then)/60)) 
      logging.info('Saving U-map')
      utils.viz_som(som_model, self.config.MODEL_DIR)
      logging.info("Generating Baseline Metrics")

      dist = []
      for i in tqdm(to_put_train):
          dist.append(utils.get_anomaly_Sscore(som_model,i))

      meta_data = (np.mean(dist), np.std(dist), np.max(dist),np.min(dist))
      model_to_save = [som_model, meta_data]
      utils.save_model(model_to_save, self.config.MODEL_PATH)
      T_Now = time.time()
      logging.info("Whole Process takes %s minutes", ((T_Now-T_Then)/60))

      return 0

  def infer(self):
    c = utils.load_map(self.config.MODEL_PATH)
    w2v_model_stored = utils.load_map(self.config.W2V_MODEL_PATH)

    som_model = c[0]
    meta_data = c[1]
    maxx = meta_data[2]
    stdd = meta_data[1]

    logging.info("Models loaded, running %d infer loops" % self.config.INFER_LOOPS)

    for i in range(self.config.INFER_LOOPS):
      then = time.time()
      now = datetime.datetime.now()

      #Get data for inference
      data, json_logs = self.storage.retrieve(self.config.INFER_TIME_SPAN, self.config.INFER_MAX_ENTRIES)
      
      logging.info("%d logs loaded from the last %d seconds", len(data) , self.config.INFER_TIME_SPAN)

      if len(data) == 0:
        logging.info("There are no logs for this service in the last %s seconds", self.config.INFER_TIME_SPAN)
        logging.info("waiting for next minute to start...")
        logging.info("press ctrl+c to stop process")
        nown = time.time()
        time.sleep(60-(nown-then))
        continue     

      logging.info("Preprocessing logs")

      for lines in range(len(data)):
        data["_source.message"][lines] = utils.clean_message(data["_source.message"][lines]) 

      try:
        new_D, _ = utils.update_w2v_models(w2v_model_stored, data)
      except KeyError:
        logging.error("Word2Vec model fields incompatible with current log set. Retrain model with log data from the same service")
        exit()
      
      transforms = utils.transform_text(w2v_model_stored, new_D)
      v = utils.one_vector(transforms)

      dist = []
      for i in v:
        dist.append(utils.get_anomaly_Sscore(som_model,i))
      
      f = []
      for i in range(len(data)):
        s = json_logs[i]["_source"]  # This needs to be more general, only works for ES incoming logs right now. 
        s['anomaly_score'] = dist[i] 

        if dist[i] > (self.config.ANOMALY_THRESHOLD*maxx): 
          s['anomaly'] = 1

        else:
          s['anomaly'] = 0

        f.append(s)
          
      self.storage.store_results(f)
        #print(res)

          # Also push to CSV for Human-In-Loop Portion

          #d = {"label":"not reviewed"}
          #f = pd.DataFrame(d, index = range(1))
          #data = new_D.loc[loc:loc].join(f)
          #data["label"] = 0;

          #if os.path.isfile("found_anomalies.csv") == False:
          #	with open("found_anomalies.csv", "a") as f:
          #		data.to_csv(f,header = True)

          #else:
          #	with open("found_anomalies.csv", "a") as f:
          #		data.to_csv(f,header = False)

      now = time.time()
      logging.info("Analyzed one minute of data in %s seconds",(now-then))
      logging.info("waiting for next minute to start...") 
      logging.info("press ctrl+c to stop process")
      sleep_time = self.config.INFER_TIME_SPAN-(now-then)
      if sleep_time > 0:
        time.sleep(sleep_time)
