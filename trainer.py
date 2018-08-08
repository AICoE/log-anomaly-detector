from ut import * 

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
import pandas as pd
from sklearn.externals import joblib
from scipy.spatial.distance import cosine
import sys
import datetime 
import warnings
from tqdm import tqdm





def trainer():
    
    
    T_Then = time.time()
    warnings.filterwarnings("ignore")


    endpointUrl = os.environ.get("LADT_ELASTICSEARCH_ENDPOINT")
    model = os.environ.get("LADT_MODEL")
    index = os.environ.get("LADT_INDEX")
    time_span = os.environ.get("LADT_TIME_SPAN")
    max_entries = int(os.environ.get("LADT_MAX_ENTRIES"))
    itters = int(os.environ.get("LADT_ITERS"))
    service = os.environ.get("LADT_SERVICE")

    
    up = os.path.isfile("models/"+model)
    if up == True:
        m = Load_Map("models/"+model)
        m = m[0]
        mod = Load_Map("models/W2V.models")
    else:
        m = 0




    now = datetime.datetime.now()
    date = now.strftime("%Y.%m.%d")

    #endpointUrl = 'http://elasticsearch.perf.lab.eng.bos.redhat.com:9280'
    #index = 'logstash-'+date
    index = index+date



    print("Reading in Logs from ", endpointUrl)
    logs = get_data_from_ES(endpointUrl,index, service, max_entries, time_span)

    print(len(logs['hits']['hits']), "logs loaded in from last ", time_span, " seconds")


    if len(logs['hits']['hits']) == 0:
        print("There are no logs for this service in the last ", time_span, " seconds")
        print("Waiting 60 seconds and trying again")
        time.sleep(60)
        trainer()
        return 





    print("Preprocessing logs & Cleaning Messages")

    new_D = json_normalize(logs['hits']['hits'])

    for lines in range(len(new_D["_source.message"])):
        new_D["_source.message"][lines] = Clean(new_D["_source.message"][lines]) 

    # Below code for user feedback    
    # if os.path.isfile("found_anomalies.csv") == True:

    #     f = pd.read_csv("found_anomalies.csv")
    #     extra = f[f["label"] == 0]
    #     extra = extra.drop("label", axis=1)
    #     extra = extra.drop("Unnamed: 0", axis = 1)
    #     new_D.append(extra)

    
    print("Learning Word2Vec Models and Saving for Inference Step")

    then = time.time()
    
    

    if up == False:
        models, new_D = Make_Models(new_D,True)

    else:
        models = mod
        new_D, models = Update_W2V_Models(mod,new_D)
        joblib.dump(models,"models/W2V.models")




    now = time.time()

    print("Training and Saving took",(now-then)/60,"Minutes")

    print("Encoding Text Data")

    transforms = Transform_Text(models,new_D)

    to_put_train = One_Vector(transforms)
    
    print("Start Training SOM...")
    then = time.time()

    if up== False:
        m = np.random.rand(24,24,to_put_train.shape[1])
    else: 
        pass
    
    mapp = SOM(to_put_train,24,itters, m)
    now = time.time()

    print("Training took ",(now-then)/60, "minutes")

    print('Saving U-map')

    Viz_SOM(mapp)

    print("Generating Baseline Metrics")

    dist = []
    for i in tqdm(to_put_train):
        dist.append(Get_Anomaly_Score(mapp,i))

    meta_data = (np.mean(dist), np.std(dist), np.max(dist),np.min(dist))

    model_to_save = [mapp, meta_data]

    Save_Model(model_to_save,"map.sav")

    T_Now = time.time()

    print("Whole Process takes ",(T_Now-T_Then)/60, "minutes")



if __name__ == "__main__":
    trainer()