from elasticsearch2 import Elasticsearch
import re
from gensim.models import Word2Vec
import json
import time
import os
import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt
import numpy as np
from pandas.io.json import json_normalize
from sklearn.externals import joblib
from scipy.spatial.distance import cosine
import datetime
import logging


logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO) 


###################Word 2 Vec#####################

def clean_message(msg):
    """
    function to remove all none alphabetical characters from message strings.
    """
    return "".join(re.findall("[a-zA-Z]+", msg))


def make_models(words, save=True, filename='W2V.models'):
    """
    """

    words = words.fillna("EMPTY")

    keys = []

    for x in list(words.columns):
    	if "_source" in x:
    		keys.append(x)

    models = {}
    for col in keys:  
        try:
            models[col] = Word2Vec([list(words[col])],min_count=1,size=50)
        except:
            fix = ["".join(p) for p in list(words[col])]
            words[col] = fix
            models[ col] = Word2Vec([fix], min_count=1, size=50)

        #print(col)
    if save:
    	joblib.dump(models, filename)
    
    return models, words


def transform_text(models, new_D):
    transforms = {}
    for col in list(models.keys()):
        transforms[col] = models[col].wv[new_D[col]]
    
    return transforms


def update_w2v_models(models, words):
	words = words.fillna('EMPTY')

	for m in list(models.keys()):
		try:
			(models[m]).build_vocab([words[m]],update=True)
		except:
			fix = ["".join(p) for p in list(words[m])]
			words[m] = fix
			(models[m]).build_vocab([fix], update=True)

	logging.info("Models Updated")
	return words, models
    
def one_vector(model): 
    column = list(model.keys())
    new_data = []

    for i in range(len(model['_source.message'])):
        logc = np.array(0)
        for k in column:
            c = model[k]
            try:
                a = np.array(c[i])
                logc = np.append(logc,a)

            except IndexError:
                a = np.array([0,0,0,0,0])
                logc = np.append(logc,a)
        new_data.append(logc)

    return np.array(new_data,ndmin=2)



######################################################

######################## SOM #########################

def save_model(mapp, filename):
    joblib.dump(mapp, filename)


def load_map(filename):
    f = joblib.load(filename) 
    return f   


def get_anomaly_Sscore(som, log):
        # convert log into vector using same word2vec model (here just going to grab from existing)
    dist_smallest = np.inf
    for x in range(som.shape[0]):
        for y in range(som.shape[1]):
            dist = np.linalg.norm(som[x][y]-log) #cosine(som[x][y],log)#np.linalg.norm(som[x][y]-log)
            if dist < dist_smallest:
                   dist_smallest = dist
                   
    return dist_smallest


def viz_som(mapp, dest):
	# Since Data is no longer representable in 2 or 3 dimensions we will display a matrix of distances from adjecent vectors
    new = np.zeros((24,24))

    for x in range(mapp.shape[0]):
        for y in range(mapp.shape[1]):
                spot = mapp[x][y]
                
                try:
                    for i in range(-1,2):
                        for j in range(-1,2):
                            new[x][y] += np.linalg.norm(spot-mapp[x+i][y+j]) #cosine(spot, mapp[x+i][y+j])#
                            
                except IndexError:

                    pass

    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(new, interpolation='nearest')
    fig.colorbar(cax)
    fig.savefig(os.path.join(dest, 'U-map.png'))



###################################################################