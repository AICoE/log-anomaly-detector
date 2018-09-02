import datetime
from pandas.io.json import json_normalize
import json
import os

from .storage import Storage
from ..config import Configuration

import logging

logging.basicConfig(format = '%(levelname)s: %(message)s' , level= logging.INFO)

class LocalStorage(Storage):

	NAME = "local"
	
	def __init__(self, configuration):
		self.config = configuration
		configuration.storage = LSConfiguration()

	def retrieve(self, time_range, number_of_entries):
		with open(self.config.storage.LS_INPUT_PATH, 'r') as fp:
			data = json.load(fp)
		
		data_set = json_normalize(data)

		if len(data_set) > number_of_entries:
			data_set = data_set[:-number_of_entries]
		logging.info("%d logs loaded", len(data_set))

		return data_set, len(data_set) # bad solution, this is how Entry objects could come in. 

	def store_results(self, data): #Should take in a Batch_Entries object
		with open(self.config.storage.LS_OUTPUT_PATH, 'w') as fp:
			json.dump(data, fp)

class LSConfiguration(Configuration):
	LS_INPUT_PATH = ""
	LS_OUTPUT_PATH = ""

	def __init__(self):
		self.load()
