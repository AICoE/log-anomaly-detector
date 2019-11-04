"""Storage Attribute for data query storage provider."""


class DefaultStorageAttribute:
    """Local Storage Attribute only requires false_positive data which is optional."""

    def __init__(self, false_data=None):
        """Local Storage only takes an optional field of false_positive."""
        self._false_data = false_data

    @property
    def false_data(self):
        """Set false positive data."""
        return self._false_data

    @false_data.setter
    def false_data(self, x):
        """Get false positive data."""
        self._false_data = x


class ESStorageAttribute(DefaultStorageAttribute):
    """Elastic Search Attributes require false positive data and time_range and number of entries to pull."""

    def __init__(self, time_range: int, number_of_entries: int, false_data=None):
        """Set initial properties for required fields when fetching data from ES."""
        super().__init__(false_data)
        self.__time_range = time_range
        self.__number_of_entries = number_of_entries
        self.false_data = false_data

    @property
    def time_range(self):
        """Time range for query."""
        return self.__time_range

    @time_range.setter
    def time_range(self, x):
        """Time range for query."""
        self.__time_range = x

    @property
    def number_of_entries(self):
        """Max number of entries for query."""
        return self.__number_of_entries

    @number_of_entries.setter
    def number_of_entries(self, x):
        """Time range for query and max number of entries."""
        self.__number_of_entries = x
