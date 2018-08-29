import datetime
from pandas.io.json import json_normalize
import json

from storage.storage import Storage
from storage.local_batch_entry import Local_Batch_Entry

class Local_Storage(Storage):

	def __init__(self,path_in, path_out):
		
		self.path_in = path_in
		self.path_out = path_out


	def retrieve(self):
		
		with open(self.path_in) as f:
			data = json.load(f)


		
		data_set = json_normalize(data)
		DATA = Local_Batch_Entry(data_set)

		return DATA, data # bad solution, this is how Entry objects could come in. 

	def store_results(self, data): #Should take in a Batch_Entries object
		
		with open(self.path_out, 'w') as outfile:
			json.dump(data,outfile)

######################################################################