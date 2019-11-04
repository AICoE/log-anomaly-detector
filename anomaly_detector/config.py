"""Configuration setting class."""

import os
import distutils
import logging
import yaml

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


class Configuration:
    """Main configuration class which is contains the config values."""

    FACT_STORE_URL = ""
    FREQ_NOISE = 1
    # One of the storage backends available in storage/ dir
    STORAGE_DATASOURCE = "local"
    STORAGE_DATASINK = "local"
    # Location of local data
    # A directory where trained models will be stored
    MODEL_DIR = "./models/"
    MODE_DIR_CALLABLE = check_or_create_model_dir
    # Name of the file where SOM model will be stored
    MODEL_FILE = "SOM.model"
    # Name of the file where W2V model will be stored
    W2V_MODEL_FILE = "W2V.model"
    MODEL_PATH_CALLABLE = join_model_path
    MODEL_PATH = ""
    W2V_MODEL_PATH_CALLABLE = join_w2v_model_path
    W2V_MODEL_PATH = ""
    # Custom parameters for W2V
    W2V_MIN_COUNT = 1
    W2V_ITER = 5
    W2V_COMPUTE_LOSS = False
    W2V_SEED = 1
    W2V_WORKERS = 3
    # Custom parameters for SOM
    SOMPY_TRAIN_ROUGH_LEN = 100
    SOMPY_TRAIN_FINETUNE_LEN = 5
    SOMPY_NODE_MAP = 24
    SOMPY_INIT = "pca"

    MODEL_STORE = ""
    MODEL_STORE_PATH = "anomaly-detection/models/"
    # Number of seconds specifying how far to the past to go to load log entries for training
    TRAIN_TIME_SPAN = 900
    # Maximum number of entries for training loaded from backend storage
    TRAIN_MAX_ENTRIES = 315448
    # Number of SOM training iterations
    TRAIN_ITERATIONS = 315448
    # If true, re-traing the models
    TRAIN_UPDATE_MODEL = False
    # Set the window size for word2Vec training
    TRAIN_WINDOW = 5
    # Set the length of the encoded log vectors
    TRAIN_VECTOR_LENGTH = 25
    # number of jobs to use to parallelize the training, should match cpu resource limit
    PARALLELISM = 2

    # Threshold used to decide whether an entry is an anomaly
    INFER_ANOMALY_THRESHOLD = 3.1
    # Number of seconds specifying how far in the past to go to load log entries for inference
    INFER_TIME_SPAN = 60
    # Number of inferences before retraining the models
    INFER_LOOPS = 10
    # Maximum number of entries to be loaded for inference
    INFER_MAX_ENTRIES = 78862

    # S3 credentials for storing model up to s3 post training.
    S3_KEY = ""
    S3_SECRET = ""
    S3_HOST = ""
    S3_BUCKET = ""
    # local test dataset
    LS_INPUT_PATH = ""
    # Name of local results data
    LS_OUTPUT_PATH = ""
    LS_OUTPUT_RWA_MODE = "w"
    # ElasticSearch endpoint URL
    ES_ENDPOINT = ""
    # Path to a directory where cert and key (es.crt and es.key) are stored for authentication
    ES_CERT_DIR = ""
    # If True, connect using ssl
    ES_USE_SSL = True
    # If True, verify SSL certificates
    ES_VERIFY_CERTS = False
    # ElasticSearch index name where results will be pushed to
    ES_TARGET_INDEX = ""
    # ElasticSearch index name where log entries will be pulled from
    ES_INPUT_INDEX = ""
    # JSON representing a query passed to data source to match the data
    LOG_FORMATTER = ""
    # When customer has custom log format. We will need to perform custom processing.
    ES_QUERY = ""
    ES_VERSION = 5
    KF_BOOTSTRAP_SERVER = ""
    KF_TOPIC = ""
    KF_CACERT = None
    KF_SECURITY_PROTOCOL = 'PLAINTEXT'
    KF_AUTO_TIMEOUT = 30000
    ES_ELAST_ALERT = 1
    OS_NAMESPACE = os.getenv("OPENSHIFT_BUILD_NAMESPACE", "localhost")
    prefix = "LAD"

    def __init__(self, prefix=None, config_yaml=None):
        """Initialize configuration."""
        # For backward compatibility
        self.load_from_env()
        if config_yaml is not None:
            with open(config_yaml) as f:
                yaml_data = yaml.load(f, Loader=yaml.FullLoader)
                for prop in self.__class__.__dict__.keys():
                    attr = getattr(self, prop)
                    if prop.isupper() and prop.endswith("_CALLABLE") and callable(attr):
                        attr()
                    elif prop.isupper() and prop in list(yaml_data.keys()):
                        self.set_property(prop, yaml_data[prop])
                        # self.__setattr__(prop, yaml_data[prop])
        else:
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
            self.set_property(prop, val)

        for prop in self.__class__.__dict__.keys():
            attr = getattr(self, prop)
            if prop.isupper() and prop.endswith("_CALLABLE") and callable(attr):
                attr()

    def set_property(self, prop, val):
        """Set the correct datatype."""
        typ = type(getattr(self, prop))
        if val is not None:

            if typ is int:
                setattr(self, prop, int(val))
            elif typ is float:
                setattr(self, prop, float(val))
            elif typ is str:
                setattr(self, prop, str(val))
            elif typ is bool:
                if type(val) is bool:
                    setattr(self, prop, val)
                else:
                    setattr(self, prop, bool(distutils.util.strtobool(val)))
            else:
                raise Exception("Incorrect type for %s (%s) loaded " % (prop, typ))
