from ut import * 
from elasticsearch2 import Elasticsearch, helpers
from gensim.models import Word2Vec
from SOM import SOM 
import json
import os
import numpy as np
from pandas.io.json import json_normalize
from sklearn.externals import joblib
from scipy.spatial.distance import cosine
import datetime
import logging

#from storage.es_storage import ES_Storage
from storage.local_storage import Local_Storage

logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO)

# making chnages to the OOP branch

def infer():


	endpointUrl = os.environ.get("LADI_ELASTICSEARCH_ENDPOINT")
	outpoint_prefix = os.environ.get("LADI_TARGET_INDEX")
	model = os.environ.get("LADI_MODEL")
	model_path = os.environ.get("LADT_MODEL_DIR")
	index_prefix = os.environ.get("LADI_INDEX")
	time_span = int(os.environ.get("LADI_TIME_SPAN"))
	max_entries = int(os.environ.get("LADI_MAX_ENTRIES"))
	service = os.environ.get("LADI_SERVICE")
	threshold = float(os.environ.get("LADI_THRESHOLD"))
	infer_loops = int(os.environ.get("LADT_TRAIN_LAG"))

	c = Load_Map(model_path  +"/" +  model)
	mod = Load_Map(model_path +"/W2V.models")

	mapp = c[0]
	meta_data = c[1]
	maxx = meta_data[2]
	stdd = meta_data[1]



	for i in range(infer_loops):

		then = time.time()
		now = datetime.datetime.now()

		get data and convert to a pandas DF
		E = ES_Storage(endpointUrl,index_prefix,service,outpoint_prefix)
		E.add_time()
		data, json_logs = E.retrieve(time_span,max_entries)

		#L = Local_Storage("/home/mcliffor/Desktop/toy_data.json","/home/mcliffor/Desktop/test_output.json")
		#data, json_logs = L.retrieve()





		logging.info("Reading in Logs from %s", endpointUrl)
		logging.info("%s logs loaded from the last %s seconds", str(data.get_length()) , time_span)

		if data.get_length() == 0:
			
			logging.info("There are no logs for this service in the last %s seconds", time_span)
			logging.info("waiting for next minute to start...")
			logging.info("press ctrl+c to stop process")
			nown = time.time()
			time.sleep(60-(nown-then))
			continue
			

		logging.info("Preprocessing logs")

		for lines in range(data.get_length()):
			data.Data["_source.message"][lines] = Clean(data.Data["_source.message"][lines]) 

		try:
			new_D, nothing = Update_W2V_Models(mod,data.Data)
		except KeyError:
			logging.error("Word2Vec model fields incompatible with current log set. Retrain model with log data from the same service")
			exit()



		
		transforms = Transform_Text(mod,new_D)
		v = One_Vector(transforms)

		dist = []
		for i in v:
			dist.append(Get_Anomaly_Score(mapp,i))
		
		f = []
		for i in range(data.get_length()):
			s = json_logs[i]["_source"]  # This needs to be more general, only works for ES incoming logs right now. 
			#s = json_logs[i] # for local_storage
			s['anomaly_score'] = dist[i] 

			if dist[i] > (threshold*maxx): 
				s['anomaly'] = 1

			else:
				s['anomaly'] = 0

			f.append(s)
				
		#L.store_results(f)
		E.store_results(f)
			#print(res)

				# Also push to CSV for Human-In-Loop Portion

				#d = {"label":"not reviewed"}
				#f = pd.DataFrame(d, index = range(1))
				#data = new_D.loc[loc:loc].join(f)
				#data["label"] = 0;

				#if os.path.isfile("found_anomalies.csv") == False:
				#	with open("found_anomalies.csv", "a") as f:
				#		data.to_csv(f,header = True)

				#else:
				#	with open("found_anomalies.csv", "a") as f:
				#		data.to_csv(f,header = False)

		now = time.time()
		logging.info("Analyzed one minute of data in %s seconds",(now-then))
		logging.info("waiting for next minute to start...") 
		logging.info("press ctrl+c to stop process")
		time.sleep(time_span-(now-then))



if __name__ == "__main__":
    infer()
