"""
"""

import os
import distutils

import logging

_LOGGER = logging.getLogger(__name__)


def join_model_path(config):
    """Construct model path."""
    config.MODEL_PATH = os.path.join(config.MODEL_DIR, config.MODEL_FILE)


def join_w2v_model_path(config):
    """Construct a word2vec model path."""
    config.W2V_MODEL_PATH = os.path.join(config.MODEL_DIR, config.W2V_MODEL_FILE)


def check_or_create_model_dir(config):
    """Check if model dir exists and create if not."""
    if not os.path.exists(config.MODEL_DIR):
        os.mkdir(config.MODEL_DIR)


class Configuration():
    """
    Configuration object.
    
    Properties which names are all caps are used for configuration of the application.

    If the name contains _CALLABLE suffix, it is called after the environment variables are loaded
    """

    # One of the storage backends available in storage/ dir
    STORAGE_BACKEND = "local"
    # Location of local data
    LOCAL_DATA_FILE = os.environ['LOCAL_DATA_FILE']
    # Name of local results data
    LOCAL_RESULTS_FILE = os.environ['LOCAL_RESULTS_FILE']
    # A directory where trained models will be stored
    MODEL_DIR = "./models/"
    MODE_DIR_CALLABLE = check_or_create_model_dir
    # Name of the file where SOM model will be stored TODO: move to model config
    MODEL_FILE = "SOM.model"
    # Name of the file where W2V model will be stored TODO: move to model config
    W2V_MODEL_FILE = "W2V.model"
    MODEL_PATH_CALLABLE = join_model_path
    MODEL_PATH = ""
    W2V_MODEL_PATH_CALLABLE = join_w2v_model_path
    W2V_MODEL_PATH = ""
    MODEL_STORE= ""
    MODEL_STORE_PATH = 'anomaly-detection/models/'

    # Number of seconds specifying how far to the past to go to load log entries for training TODO: move to es storage backend
    TRAIN_TIME_SPAN = 900
    # Maximum number of entries for training loaded from backend storage
    TRAIN_MAX_ENTRIES = 10000
    # Number of SOM training iterations TODO: move to model config
    TRAIN_ITERATIONS = 4500
    # If true, re-traing the models
    TRAIN_UPDATE_MODEL = False
    # Set the window size for word2Vec training
    TRAIN_WINDOW = 5
    # Set the length of the encoded log vectors
    TRAIN_VECTOR_LENGTH = 25

    # Threshold used to decide whether an entry is an anomaly
    INFER_ANOMALY_THRESHOLD = 3.1
    # Number of seconds specifying how far in the past to go to load log entries for inference TODO: move to es storage backend
    INFER_TIME_SPAN = 60
    # Number of inferences before retraining the models
    INFER_LOOPS = 10
    # Maximum number of entries to be loaded for inference
    INFER_MAX_ENTRIES = 10000

    prefix = "LAD"

    def __init__(self, prefix=None):
        """Initialize configuration."""
        self.storage = None
        if prefix:
            self.prefix = prefix
        self.load()

    def load(self):
        """Load the configuration."""
        _LOGGER.info("Loading %s" % self.__class__.__name__)
        self.load_from_env()

    def load_from_env(self):
        """Load the configuration from environment."""
        for prop in self.__class__.__dict__.keys():
            if not prop.isupper():
                continue
            env = "%s_%s" % (self.prefix, prop)
            val = os.environ.get(env)
            typ = type(getattr(self, prop))
            if val:
                _LOGGER.info("Loading %s from environment as %s" % (env, typ))
                if typ is int:
                    setattr(self, prop, int(val))
                elif typ is float:
                    setattr(self, prop, float(val))
                elif typ is str:
                    setattr(self, prop, str(val))
                elif typ is bool:
                    setattr(self, prop, bool(distutils.util.strtobool(val)))
                else:
                    raise Exception("Incorrect type for %s (%s) loaded from env %s" % (prop, typ, env))

        for prop in self.__class__.__dict__.keys():
            attr = getattr(self, prop)
            if prop.isupper() and prop.endswith("_CALLABLE") and callable(attr):
                attr()
