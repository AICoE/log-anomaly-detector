"""
"""

import numpy as np
from gensim.models import Word2Vec

from .base_model import BaseModel

import logging

_LOGGER = logging.getLogger(__name__)


class W2VModel(BaseModel):
    """Word2Vec model wrapper."""

    def update(self, words):
        """Update existing w2v model."""
        words = words.fillna('EMPTY')

        for col in list(self.model.keys()):
            if col in words:
                self.model[col].build_vocab([words[col]], update=True)
            else:
                _LOGGER.warning("Skipping key %s as it does not exist in 'words'" % col)
        _LOGGER.info("Models Updated")
        return words, self.model

    def create(self, words):
        """Create new word2vec model."""
        words = words.fillna("EMPTY")

        self.model = {}
        for col in words.columns:
            if col in words:
                self.model[col] = Word2Vec([list(words[col])], min_count=1, size=50)
            else:
                _LOGGER.warning("Skipping key %s as it does not exist in 'words'" % col)

        return words, self.model

    def one_vector(self, new_D):
        """Create a single vector from model."""
        transforms = {}
        for col in self.model.keys():
            print(new_D[col][0])
            print(self.model[col].wv[new_D[col]][0])
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