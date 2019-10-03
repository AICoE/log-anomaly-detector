"""Storage Data Source."""
from abc import ABCMeta, abstractmethod


class StorageSource(metaclass=ABCMeta):
    """Base class for storage implementations."""

    def __init__(self, configuration):
        """Initialize storage."""
        self.config = configuration

    @abstractmethod
    def retrieve(self, storage_attribute):
        """Retrieve data from storage and return them as a pandas dataframe."""
        raise NotImplementedError("Please implement the <retrieve method>")
