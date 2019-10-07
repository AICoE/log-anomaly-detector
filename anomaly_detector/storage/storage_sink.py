"""Storage Data Sink."""
from abc import ABCMeta, abstractmethod


class StorageSink(metaclass=ABCMeta):
    """Base class for storage implementations."""

    def __init__(self, configuration):
        """Initialize storage."""
        self.config = configuration

    @abstractmethod
    def store_results(self, entries):
        """Store results back to storage backend."""
        raise NotImplementedError("Please implement the <store_results method>")
