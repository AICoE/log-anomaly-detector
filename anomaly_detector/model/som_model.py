import os
import numpy as np
from tqdm import tqdm 

import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt

from .base_model import BaseModel

class SOMModel(BaseModel):
  def train(self, inp, map_size, iterations):
    if self.model is None:
      self.model = np.random.rand(map_size, map_size, inp.shape[1]) # Generate a 24x24 node feature of color data

    for iters in tqdm(range(iterations)): 
      rand_num = np.random.randint(inp.shape[0])
      current_vector = inp[rand_num,:] # Select a Random Document Vector From the training data

      # Traverse the map and calculating Euclidian Distance from each node to find best matching unit (BMU)
      bmu = np.inf
      bmu_loc = (0,0)

      for i in range(self.model.shape[0]):
        for j in range(self.model.shape[1]):
          dist = np.linalg.norm(current_vector-self.model[i][j])
          if dist < bmu:
            bmu = dist
            bmu_loc = (i,j)

        # Update BMU and Neighbours in the map: 
      try:
        for x in range(-12,12):
          for y in range(-12,12):                
            self.model[bmu_loc[0]+x][bmu_loc[1]+y] = self.model[bmu_loc[0]+x][bmu_loc[1]+y] + (self.alph(iterations, iters)) * \
                                                     self.neihborhood(np.array(bmu_loc), np.array([bmu_loc[0]+x, bmu_loc[1]+y])) * (current_vector - self.model[bmu_loc[0]+x][bmu_loc[1]+y])
      except IndexError:
        pass

  def save_visualisation(self, dest):
    # Since Data is no longer representable in 2 or 3 dimensions we will display a matrix of distances from adjecent vectors
    new = np.zeros((24,24))

    for x in range(self.model.shape[0]):
      for y in range(self.model.shape[1]):
        spot = self.model[x][y]
        try:
          for i in range(-1,2):
            for j in range(-1,2):
              new[x][y] += np.linalg.norm(spot - self.model[x+i][y+j]) #cosine(spot, mapp[x+i][y+j])#                    
        except IndexError:
          pass

    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(new, interpolation='nearest')
    fig.colorbar(cax)
    fig.savefig(os.path.join(dest, 'U-map.png'))

  def get_anomaly_score(self, log):
        # convert log into vector using same word2vec model (here just going to grab from existing)
    dist_smallest = np.inf
    for x in range(self.model.shape[0]):
      for y in range(self.model.shape[1]):
        dist = np.linalg.norm(self.model[x][y]-log) #cosine(som[x][y],log)#np.linalg.norm(som[x][y]-log)
        if dist < dist_smallest:
          dist_smallest = dist

    return dist_smallest

  @classmethod
  def alph(cls, T, t): # Learning Rate, Deacrease as we move through the iterations
    if T == 0:
      return 0

    return (T-t)/T

  @classmethod
  def neihborhood(cls, bmu_location, node_location): # Neighborhood function, dictates the maganitude of the update as we move away from the BMU
    dist = np.linalg.norm(bmu_location-node_location)
    return np.exp(-1.0*(dist/2))
