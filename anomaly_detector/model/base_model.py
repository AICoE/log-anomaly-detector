from sklearn.externals import joblib
import os

class BaseModel():
  def __init__(self):
    self.model = None
    self.metadata = None

  def load(self, source):
    loaded_model = joblib.load(source)
    self.model = loaded_model['model']
    self.metadata = loaded_model['metadata']

  def save(self, dest):
    saved_model = {
      'model': self.model, 
      'metadata': self.metadata
    }
    joblib.dump(saved_model, dest)

  def get(self):
    return self.model

  def set(self, model):
    self.model = model

  def get_metadata(self):
    return self.metadata

  def set_metadata(self, metadata):
    self.metadata = metadata