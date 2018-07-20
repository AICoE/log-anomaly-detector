from elasticsearch2 import Elasticsearch
import re
from gensim.models import Word2Vec
from SOM import SOM 
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




###########Elastic Search Methods ################

default_query =  {'query': {'match': {'service': 'journal'}},
         		"filter" : {"range": {"@timestamp": {"gte": "now-2s","lte": "now"}}},
                 'sort':{'@timestamp':{'order':'desc'}},
                "size":20 #size is more critical than "terminate_after" to limit query size!!!
                }

def get_data_from_ES(endpoint, index,num = 20, time = 2, query = default_query):
    
    es = Elasticsearch(endpoint)
    query['size'] = num
    query['filter']['range']['@timestamp']['gte'] = 'now-'+str(time)+'s'

    return es.search(index, body=json.dumps(query))




##################################################

###################Word 2 Vec#####################

def Clean(x):
	return "".join(re.findall("[a-zA-Z]+",x))


def Make_Models(DF, Save = False, filename = 'W2V.models'):
    models = {}
    for col in list(DF.keys()):  
        try:
            models[col] = Word2Vec([list(DF[col])],min_count=1,size=50)
        except:
            print(col, " not Currently Vectorized")


    if Save == True:
    	joblib.dump(models, filename)
    
    return models


def Transform_Text(models, new_D):

    transforms = {}
    for col in list(models.keys()):
        transforms[col] = models[col].wv[new_D[col]]
    
    return transforms


def Update_W2V_Models(models,new_words):
	for m in list(models.keys()):
		(models[m]).build_vocab([new_words[m]],update=True)

	print("Models Updated")





def Word2Vectorizer(sq,data,column, path = ''): # Dont think I need this Delete or update by EOD
    rdd = sq.createDataFrame(data[column],[column])
    word2vec = Word2Vec(vectorSize=5, minCount=1, inputCol=column, outputCol="result"+column)
    model = word2vec.fit(rdd)
    model.write().overwrite().save(path+"result"+column)
    #model = model.transform(rdd)
    return model


    
def One_Vector(model):
        
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
                    print("nO!!")
                    a = np.array([0,0,0,0,0])
                    logc = np.append(logc,a)




            new_data.append(logc)
            
    return np.array(new_data,ndmin=2)



######################################################

######################## SOM #########################

def Save_Model(mapp, filename):
    joblib.dump(mapp, filename)


def Load_Map(filename):
    f = joblib.load(filename) 
    return f   


def Get_Anomaly_Score(som,log):
        # convert log into vector using same word2vec model (here just going to grab from existing)
    dist_smallest = np.inf
    for x in range(som.shape[0]):
        for y in range(som.shape[1]):
            dist = np.linalg.norm(som[x][y]-log) #cosine(som[x][y],log)#np.linalg.norm(som[x][y]-log)
            if dist < dist_smallest:
                   dist_smallest = dist
                   
    return dist_smallest


def Viz_SOM(mapp):
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
   fig.savefig('U-map.png')



###################################################################