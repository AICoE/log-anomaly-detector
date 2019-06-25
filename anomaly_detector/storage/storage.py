"""Storage abstract class."""

from abc import ABCMeta, abstractmethod

import re


class Storage(metaclass=ABCMeta):
    """Base class for storage implementations."""

    def __init__(self, configuration):
        """Initialize storage."""
        self.config = configuration

    @abstractmethod
    def retrieve(self, storage_attribute):
        """Retrieve data from storage and return them as a pandas dataframe."""
        raise NotImplementedError("Please implement the <retrieve method>")

    @abstractmethod
    def store_results(self, entries):
        """Store results back to storage backend."""
        raise NotImplementedError("Please implement the <store_results method>")

    @classmethod
    def _clean_message(cls, line):
        """Remove all none alphabetical characters from message strings."""
        return "".join(
            re.findall("[a-zA-Z]+", line)
        )  # Leaving only a-z in there as numbers add to anomalousness quite a bit

    @classmethod
    def _preprocess(cls, data):
        """Provide preprocessing for the data before running it through W2V and SOM."""
        def to_str(x):
            """Convert all non-str lists to string lists for Word2Vec."""
            ret = " ".join([str(y) for y in x]) if isinstance(x, list) else str(x)
            return ret

        for col in data.columns:
            if col == "message":
                data[col] = data[col].apply(cls._clean_message)
            else:
                data[col] = data[col].apply(to_str)

        data = data.fillna("EMPTY")
