from storage.batch_entry import Batch_Entry

class ES_Batch_Entry(Batch_Entry):

	def __init__(self,Data):
		self.Data = Data

	def get_length(self):

		return len(self.Data)

	def show_data(self):
		print(self.Data)