from abc import abstractmethod, ABCMeta

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