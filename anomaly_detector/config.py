import os

import logging

_LOGGER = logging.getLogger(__name__)

def join_model_path(config):
  config.MODEL_PATH = os.path.join(config.MODEL_DIR, config.MODEL_FILE)

def join_w2v_model_path(config):
  config.W2V_MODEL_PATH = os.path.join(config.MODEL_DIR, config.W2V_MODEL_FILE)

def check_or_create_model_dir(config):
  if not os.path.exists(config.MODEL_DIR):
    os.mkdir(config.MODEL_DIR)

class Configuration():
  STORAGE_BACKEND = "local"
  MODEL_DIR = "./models/"
  MODE_DIR_CALLABLE=check_or_create_model_dir
  MODEL_FILE = "SOM.model"
  W2V_MODEL_FILE = "W2V.model"
  MODEL_PATH_CALLABLE = join_model_path
  MODEL_PATH = ""
  W2V_MODEL_PATH_CALLABLE = join_w2v_model_path
  W2V_MODEL_PATH = ""

  TRAIN_TIME_SPAN = 900
  TRAIN_MAX_ENTRIES = 45000
  TRAIN_ITERATIONS = 4500
  TRAIN_UPDATE_MODEL = False

  INFER_ANOMALY_THRESHOLD = 1.1
  INFER_TIME_SPAN = 60
  INFER_LOOPS = 10
  INFER_MAX_ENTRIES = 10000
  
  prefix = "LAD"

  def __init__(self, prefix=None):
    self.storage = None
    if prefix:
      self.prefix = prefix
    self.load()

  def load(self):
    _LOGGER.info("Loading %s" % self.__class__.__name__)
    self.load_from_env()

  def load_from_env(self):
    for prop in self.__class__.__dict__.keys():
      if not prop.isupper():
        continue
      env = "%s_%s" % (self.prefix, prop)
      val = os.environ.get(env)
      typ = type(getattr(self, prop))
      if val:
        _LOGGER.info("Loading %s from environment" % env)
        if typ is int:
          setattr(self, prop, int(val))
        elif typ is float:
          setattr(self, prop, float(val))
        elif typ is str:
          setattr(self, prop, str(val))
        elif typ is bool:
          setattr(self, prop, bool(val))
        else:
          raise Exception("Incorrect type for %s (%s) loaded from env %s" % (prop, typ, env))

    for prop in self.__class__.__dict__.keys():
      attr = getattr(self, prop)
      if prop.isupper() and prop.endswith("_CALLABLE") and callable(attr):
        attr()
