
from .base_model import BaseModel

import os
import numpy as np
import logging
import sompy
from multiprocessing import Pool

_LOGGER = logging.getLogger(__name__)

class SOMPYModel(BaseModel):
    "SOMPY alternative SOM implementation with parallelization"

    def train(self, inp, map_size, iterations, parallelism):
        mapsize = [map_size, map_size]
        som = sompy.SOMFactory.build(inp, mapsize)
        som.train(n_job=parallelism)
        self.model = som.codebook.matrix.reshape([map_size,map_size, inp.shape[1]])


    def get_anomaly_score(self, logs, parallelism):

        pool = Pool(parallelism)
        dist = pool.map(self.calculate_anomaly_score, logs)
        pool.close()
        pool.join()
        return dist

    def save_visualisation(self, dest):
        return None

    def calculate_anomaly_score(self, log):
        """Compute a distance of a log entry to elements of SOM."""
        # convert log into vector using same word2vec model (here just going to grab from existing)
        dist_smallest = np.inf
        for x in range(self.model.shape[0]):
            for y in range(self.model.shape[1]):
                dist = np.linalg.norm(self.model[x][y] - log)
                if dist < dist_smallest:
                    dist_smallest = dist
        return dist