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
from sklearn.externals import joblib
from scipy.spatial.distance import cosine
import sys
import datetime 





def main(): # note: must take as userparmas model update or new, time span, and max entries, itters
    
    
    T_Then = time.time()



    try:

        model = sys.argv[1]
        time_span = sys.argv[2]
        max_entries = sys.argv[3]
        itters = int(sys.argv[4])

    
    except IndexError:
        print("\n","Insufficent arguments provided. Must provide a model name, timespan in seconds, max logs, and number of iterations for SOM training.",
            "EXAMPLE: 'python trainer.py model.sav 600 10000 10000' to update a model called model.sav  if it exisits on 600 seconds of data, with a maximum of 10000 logs and iterate over SOM 10000 times.")
        quit()

    
    try:
        m = Load_Map(model)
        m = m[0]
        up = True
        mod = Load_Map("W2V.models")
    
    except FileNotFoundError:
        m = 0
        up = False

    now = datetime.datetime.now()
    date = now.strftime("%Y.%m.%d")

    endpointUrl = 'http://elasticsearch.perf.lab.eng.bos.redhat.com:9280'
    index = 'logstash-'+date



    print("Reading in Logs from ", endpointUrl)
    logs = get_data_from_ES(endpointUrl,index, max_entries, time_span)

    print(len(logs['hits']['hits']), "logs loaded in from last ", time_span, " seconds")

    print("Preprocessing logs & Cleaning Messages")

    new_D = json_normalize(logs['hits']['hits'])

    for lines in range(len(new_D["_source.message"])):
        new_D["_source.message"][lines] = Clean(new_D["_source.message"][lines]) 


    print("Learning Word2Vec Models and Saving for Inference Step")

    then = time.time()
    
    

    if up == False:
        models, new_D = Make_Models(new_D,True)

    else:
        models = mod
        new_D, models = Update_W2V_Models(mod,new_D)
        joblib.dump(models,"W2V.models")




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
    for i in to_put_train:
        dist.append(Get_Anomaly_Score(mapp,i))

    meta_data = (np.mean(dist), np.std(dist), np.max(dist),np.min(dist))

    model_to_save = [mapp, meta_data]

    Save_Model(model_to_save,"map.sav")

    T_Now = time.time()

    print("Whole Process takes ",(T_Now-T_Then)/60, "minutes")



if __name__ == "__main__":
    main()