import datetime
from pandas.io.json import json_normalize
import json
import os
import sys

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
		data = []
		logging.info("Reading from %s" % self.config.storage.LS_INPUT_PATH)
		if self.config.storage.LS_INPUT_PATH == "-":
			cnt = 0
			for line in self._stdin():
				try:
					data.append(json.loads(line))
				except ValueError as ex:
					logging.error("Parsing failed (%s), assuming plain text" % ex)
					data.append({'_source': {'message': str(line)}})
				cnt += 1
				if cnt >= number_of_entries:
					break

			#only use _source sub-dict
			data = [x['_source'] for x in data]
			data_set = json_normalize(data)
		else:
			with open(self.config.storage.LS_INPUT_PATH, 'r') as fp:
				data = json.load(fp)
		
			data_set = json_normalize(data)

			if len(data_set) > number_of_entries:
				data_set = data_set[:-number_of_entries]
		logging.info("%d logs loaded", len(data_set))

		#Prepare data for training/inference
		self._preprocess(data_set)

		return data_set, data

	def store_results(self, data): #Should take in a Batch_Entries object
		if len(self.config.storage.LS_OUTPUT_PATH) > 0:
			with open(self.config.storage.LS_OUTPUT_PATH, 'a') as fp:
				json.dump(data, fp)
		else:
			for item in data:
				print("Anomaly: %d, Anmaly score: %f" % (item['anomaly'], item['anomaly_score']))


	@classmethod
	def _stdin(cls):
		while True:
			line = sys.stdin.readline()
			if not line:
				continue
			stripped = line.strip()
			if len(stripped):
				yield line.strip()

class LSConfiguration(Configuration):
	LS_INPUT_PATH = ""
	LS_OUTPUT_PATH = ""

	def __init__(self):
		self.load()
