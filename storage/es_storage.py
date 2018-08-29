import datetime
from pandas.io.json import json_normalize
from elasticsearch2 import Elasticsearch, helpers
import json

from storage.storage import Storage
from storage.es_batch_entry import ES_Batch_Entry

class ES_Storage(Storage):

	def __init__(self,endpoint,index_in,service, index_out):
		
		self.endpoint = endpoint
		self.index_in = index_in
		self.service = service
		self.index_out = index_out


	def add_time(self):
		# appends the correct date to the indexs
		now = datetime.datetime.now()
		date = now.strftime("%Y.%m.%d")
		self.index_in = self.index_in + date
		self.index_out = self.index_out + date


	def retrieve(self,time_range,number_of_entires):

		query =  {'query': {'match': {'service': 'journal'}},
				"filter" : {"range": {"@timestamp": {"gte": "now-2s","lte": "now"}}},
				'sort':{'@timestamp':{'order':'desc'}},
				"size":20
				}

		es = Elasticsearch(self.endpoint, timeout=30)
		query['size'] = number_of_entires
		query['filter']['range']['@timestamp']['gte'] = 'now-'+str(time_range)+'s'
		query['query']['match']['service'] = self.service
		data = es.search(self.index_in, body=json.dumps(query), request_timeout=60)
		data_set = json_normalize(data['hits']['hits'])
		DATA = ES_Batch_Entry(data_set)

		return DATA, data['hits']['hits'] # bad solution, this is how Entry objects could come in. 

	def store_results(self, data): #Should take in a Batch_Entries object 

		
		es = Elasticsearch(self.endpoint, timeout=60, max_retries=2)

		actions = [ {"_index":self.index_out,
					"_type": "log",
					"_source": data[j]}
					for j in range(len(data))]


		helpers.bulk(es,actions, chunk_size = int(len(data)/4)+1) 

######################################################################