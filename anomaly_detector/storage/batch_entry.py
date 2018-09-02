class BatchEntry:
	def __init__(self):
		self.entries = []
		pass

	def add_entry(self, entry):
		self.entries.append(entry)

	def get_entries(self):
		return self.entries

	def to_list(self):
		return [entry.get() for entry in self.entries]