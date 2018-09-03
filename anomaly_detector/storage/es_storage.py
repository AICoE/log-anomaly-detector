import datetime
from pandas.io.json import json_normalize
from elasticsearch2 import Elasticsearch, helpers
import json
import os

from .storage import Storage
from ..config import Configuration

import logging

logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO)

class ESStorage(Storage):

	NAME = "es"

	def __init__(self, configuration):
		super(ESStorage, self).__init__(configuration)
		self.config.storage = ESConfiguration()
		self.es = Elasticsearch(self.config.storage.ES_ENDPOINT, timeout=60, max_retries=2)

	def _prep_index_name(self, prefix):
		# appends the correct date to the index prefix
		now = datetime.datetime.now()
		date = now.strftime("%Y.%m.%d")
		index = prefix + date
		return index

	def retrieve(self, time_range: int, number_of_entires: int):
		index_in = self._prep_index_name(self.config.storage.ES_INPUT_INDEX)

		query =  {'query': {'match': {'service': 'journal'}},
				"filter" : {"range": {"@timestamp": {"gte": "now-2s","lte": "now"}}},
				'sort':{'@timestamp':{'order':'desc'}},
				"size":20
				}

		logging.info("Reading in max %d log entries in last %d seconds from %s", number_of_entires, time_range, self.config.storage.ES_ENDPOINT)

		
		query['size'] = number_of_entires
		query['filter']['range']['@timestamp']['gte'] = 'now-%ds' % time_range
		query['query']['match']['service'] = self.config.storage.ES_SERVICE
		es_data = self.es.search(index_in, body=json.dumps(query), request_timeout=60)
		es_data_normalized = json_normalize(es_data['hits']['hits'])

		logging.info("%d logs loaded in from last %d seconds", len(es_data_normalized), time_range)

		for lines in range(len(es_data_normalized)):
			es_data_normalized["_source.message"][lines] = self._clean_message(es_data_normalized["_source.message"][lines])

		return es_data_normalized, es_data['hits']['hits'] # bad solution, this is how Entry objects could come in. 

	def store_results(self, data): #Should take in a Batch_Entries object 
		index_out = self._prep_index_name(self.config.storage.ES_TARGET_INDEX)

		actions = [ {"_index": index_out,
					"_type": "log",
					"_source": data[i]}
					for i in range(len(data))]

		helpers.bulk(self.es, actions, chunk_size = int(len(data)/4)+1) 

class ESConfiguration(Configuration):
	ES_ENDPOINT = ""
	ES_TARGET_INDEX = ""
	ES_INPUT_INDEX = ""
	ES_SERVICE = ""
	
	def __init__(self):
		self.load()
