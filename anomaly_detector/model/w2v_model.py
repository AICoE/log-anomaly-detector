import numpy as np
from gensim.models import Word2Vec

from .base_model import BaseModel

import logging

class W2VModel(BaseModel):
  def update(self, words):
    words = words.fillna('EMPTY')

    for m in list(self.model.keys()):
      try:
        (self.model[m]).build_vocab([words[m]],update=True)
      except:
        fix = ["".join(p) for p in list(words[m])]
        words[m] = fix
        (self.model[m]).build_vocab([fix], update=True)

    logging.info("Models Updated")
    return words, self.model

  def create(self, words):
    """
    """

    words = words.fillna("EMPTY")

    keys = []

    for x in list(words.columns):
    	if "_source" in x:
    		keys.append(x)

    self.model = {}
    for col in keys:  
        try:
            self.model[col] = Word2Vec([list(words[col])],min_count=1,size=50)
        except:
            fix = ["".join(p) for p in list(words[col])]
            words[col] = fix
            self.model[col] = Word2Vec([fix], min_count=1, size=50)
    
    return words, self.model

  def one_vector(self, new_D): 
    transforms = {}
    for col in self.model.keys():
      transforms[col] = self.model[col].wv[new_D[col]]

    new_data = []

    for i in range(len(transforms['_source.message'])):
        logc = np.array(0)
        for k in transforms.keys():
            c = transforms[k]
            #try:
            logc = np.append(logc, c[i])
            #except IndexError:
            #    logc = np.append(logc, [0,0,0,0,0])
        new_data.append(logc)

    return np.array(new_data,ndmin=2)