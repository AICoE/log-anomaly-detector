"""Base model class."""
from anomaly_detector.exception import ModelLoadException, ModelSaveException
from sklearn.externals import joblib
import os


class BaseModel:
    """Base class for model implementations."""

    def __init__(self, config=None):
        """Initialize model."""
        self.model = None
        self.metadata = None
        self.config = config

    def load(self, source):
        """Load a model from disk."""
        if not os.path.isfile(source):
            raise ModelLoadException("Could not load a model. File %s does not exist" % source)

        try:
            loaded_model = joblib.load(source)
        except Exception as ex:
            raise ModelLoadException("Could not load a model: %s" % ex)

        self.model = loaded_model["model"]
        self.metadata = loaded_model["metadata"]

    def save(self, dest):
        """Save a model to disk."""
        saved_model = {"model": self.model, "metadata": self.metadata}

        try:
            joblib.dump(saved_model, dest)
        except Exception as ex:
            raise ModelSaveException("Could not save the model: %s" % ex)

    def get(self):
        """Get a model."""
        return self.model

    def set(self, model):
        """Set a model."""
        self.model = model

    def get_metadata(self):
        """Get model metadata."""
        return self.metadata

    def set_metadata(self, metadata):
        """Set model metadata."""
        self.metadata = metadata
