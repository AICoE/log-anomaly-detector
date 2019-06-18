"""Base Storage Class - Used to connect to different storage providers."""
from abc import ABCMeta, abstractmethod


class BaseStorageAdapter(metaclass=ABCMeta):
    """Base storage class for handling custom storage systems."""

    @abstractmethod
    def load_data(self):
        """Load data from storage system."""
        raise NotImplementedError("Please implement the <load_data method>")

    @abstractmethod
    def persist_data(self):
        """Persist prediction data to storage system."""
        raise NotImplementedError("Please implement the <persist_data method>")
