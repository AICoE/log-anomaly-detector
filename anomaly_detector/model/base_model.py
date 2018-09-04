from sklearn.externals import joblib
import os

from .model_exception import ModelLoadException, ModelSaveException

class BaseModel():
  def __init__(self):
    self.model = None
    self.metadata = None

  def load(self, source):
    if not os.path.isfile(source):
      raise ModelLoadException("Could not load a model. File %s does not exist" % source)

    try:
      loaded_model = joblib.load(source)
    except Exception as ex:
      raise ModelLoadException("Could not load a model: %s" % ex)

    self.model = loaded_model['model']
    self.metadata = loaded_model['metadata']

  def save(self, dest):
    saved_model = {
      'model': self.model, 
      'metadata': self.metadata
    }

    try:
      joblib.dump(saved_model, dest)
    except Exception as ex:
      raise ModelSaveException("Could not save the model: %s" % ex)

  def get(self):
    return self.model

  def set(self, model):
    self.model = model

  def get_metadata(self):
    return self.metadata

  def set_metadata(self, metadata):
    self.metadata = metadata