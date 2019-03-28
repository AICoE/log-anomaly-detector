from enum import Enum
import pprint


class Anomaly_Status(Enum):
    """
     Enumeration for indicating if an operation was successful or failed

    Allowed values include: [CORRECT, FALSE]
    """

    FALSE = 0
    CORRECT = 1

    def to_str(self):
        return pprint.pformat(self.value)

    def __repr__(self):
        return self.to_str()

    def __eq__(self, other):
        if not isinstance(other, Anomaly_Status):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other
