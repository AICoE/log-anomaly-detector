class Entry:
	def __init__(self, data):
		self.data = data
		self.process(data)

	def get_raw(self):
		return self.data

	def get(self):
		return self.content

	def process(self, data):
		self.content = data