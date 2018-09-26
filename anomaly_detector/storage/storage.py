"""
"""

from abc import abstractmethod, ABCMeta

import re


class Storage(object):
    """Base class for storage implementations."""

    __metaclass__ = ABCMeta

    NAME = "empty"

    def __init__(self, configuration):
        """Initialize storage."""
        self.config = configuration

    @abstractmethod
    def retrieve(self, time_range, number_of_entires):
        """Retrieve data from storage and return them as a pandas dataframe."""
        pass

    @abstractmethod
    def store_results(self, entries):
        """Store results back to storage backend."""
        pass

    @classmethod
    def _clean_message(cls, line):
        """Remove all none alphabetical characters from message strings."""
        return "".join(re.findall("[a-zA-Z]+", line)) # Leaving only a-z in there as numbers add to anomalousness quite a bit

    @classmethod
    def _preprocess(cls, data):
        def to_str(x):
            """Convert all non-str lists to string lists for Word2Vec."""
            ret = " ".join([str(y) for y in x]) if isinstance(x, list) else str(x)
            return ret

        for col in data.columns:
            if col == "message":
                data[col] = data[col].apply(cls._clean_message)
            else:
                data[col] = data[col].apply(to_str)

        data = data.fillna('EMPTY')
