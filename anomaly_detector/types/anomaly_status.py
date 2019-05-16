"""Anomaly Status must have typed returned objects instead of hardcoded numbers or string."""
from enum import Enum
import pprint


class Anomaly_Status(Enum):
    """Enumeration for indicating if an operation was successful or failed."""

    FALSE = 0
    CORRECT = 1

    def to_str(self):
        """Convert to string method."""
        return pprint.pformat(self.value)

    def __repr__(self):
        """Convert to string in repr method."""
        return self.to_str()

    def __eq__(self, other):
        """Check if two values are equal."""
        if not isinstance(other, Anomaly_Status):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Check if two values are not equal."""
        return not self == other
