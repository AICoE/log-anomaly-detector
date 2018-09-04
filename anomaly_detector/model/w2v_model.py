import numpy as np
from gensim.models import Word2Vec

from .base_model import BaseModel

import logging

class W2VModel(BaseModel):
  def update(self, words):
    words = words.fillna('EMPTY')

    for col in list(self.model.keys()):
      if col in words:
        self.model[col].build_vocab([words[col]], update=True)
      else:
        logging.warning("Skipping key %s as it does not exist in 'words'" % col)
    logging.info("Models Updated")
    return words, self.model

  def create(self, words):
    """
    """
    words = words.fillna("EMPTY")

    self.model = {}
    for col in words.columns:  
      if col in words:
        self.model[col] = Word2Vec([list(words[col])], min_count=1, size=50)
      else:
        logging.warning("Skipping key %s as it does not exist in 'words'" % col)
    
    return words, self.model

  def one_vector(self, new_D): 
    transforms = {}
    for col in self.model.keys():
      transforms[col] = self.model[col].wv[new_D[col]]

    new_data = []

    for i in range(len(transforms['message'])):
      logc = np.array(0)
      for _, c in transforms.items():
        if c.item(i):
          logc = np.append(logc, c[i])
        else:
          logc = np.append(logc, [0,0,0,0,0])
      new_data.append(logc)

    return np.array(new_data, ndmin=2)