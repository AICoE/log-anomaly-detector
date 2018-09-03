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