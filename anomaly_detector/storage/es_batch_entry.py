from .batch_entry import BatchEntry

class ESBatchEntry(BatchEntry):

	def __init__(self,Data):
		self.Data = Data

	def get_length(self):

		return len(self.Data)

	def show_data(self):
		print(self.Data)