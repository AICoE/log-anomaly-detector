"""SOMPY model."""
from anomaly_detector.model.base_model import BaseModel
import numpy as np
import logging
import sompy
from multiprocessing import Pool

_LOGGER = logging.getLogger(__name__)


class SOMPYModel(BaseModel):
    """SOMPY alternative SOM implementation with parallelization."""

    def __init__(self, config=None):
        """Construct with configurations for customizations."""
        super().__init__(config)
        self.config = config

    def train(self, inp, map_size, iterations, parallelism):
        """Train the SOM model."""
        mapsize = [map_size, map_size]
        som = sompy.SOMFactory.build(inp, mapsize, initialization=self.config.SOMPY_INIT)
        if not self.config:
            som.train(n_job=parallelism)
        else:
            som.train(n_job=parallelism, train_rough_len=self.config.SOMPY_TRAIN_ROUGH_LEN,
                      train_finetune_len=self.config.SOMPY_TRAIN_FINETUNE_LEN)
            # train_rough_len=100,train_finetune_len=5
        self.model = som.codebook.matrix.reshape([map_size, map_size, inp.shape[1]])

    def get_anomaly_score(self, logs, parallelism):
        """Get Anomaly Score."""
        pool = Pool(parallelism)
        dist = pool.map(self.calculate_anomaly_score, logs)
        pool.close()
        pool.join()
        return dist

    def calculate_anomaly_score(self, log):
        """Compute a distance of a log entry to elements of SOM."""
        # convert log into vector using same word2vec model (here just going to grab from existing)
        dist_smallest = np.inf
        for x in range(self.model.shape[0]):
            for y in range(self.model.shape[1]):
                dist = np.linalg.norm(self.model[x][y] - log)
                if dist < dist_smallest:
                    dist_smallest = dist
        return dist_smallest
