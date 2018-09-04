from abc import abstractmethod, ABCMeta

import re

class Storage(object): 

	__metaclass__ = ABCMeta

	NAME = "empty"

	def __init__(self, configuration):
		self.config = configuration

	@abstractmethod
	def retrieve(self, time_range, number_of_entires):
		pass

	@abstractmethod
	def store_results(self, entry):
		pass

	@classmethod
	def _clean_message(cls, line):
		"""
		function to remove all none alphabetical characters from message strings.
		"""
		return "".join(re.findall("[a-zA-Z]+", line))

	@classmethod
	def _preprocess(cls, data):
		def to_str(x):
			"""
			Convert all non-str lists to string lists for Word2Vec
			"""
			ret = " ".join([str(y) for y in x]) if isinstance(x, list) else x
			return ret

		for col in data.columns:
			if col == "message":
				data[col] = data[col].apply(cls._clean_message)
			else:
				data[col] = data[col].apply(to_str)