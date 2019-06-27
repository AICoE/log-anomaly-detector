"""Exceptions for the log anomaly detector."""


class factStoreEnvVarNotSetException(Exception):
    """Fact Store env var validator."""

    def __init__(self, msg="fact store url env var not set"):
        """Initialize message."""
        self.message = msg


class ModelLoadException(Exception):
    """Validates that model has been loaded."""

    def __intit__(self, msg="There is no existing model to load"):
        """Initialize message."""
        self.message = msg


class ModelSaveException(Exception):
    """Validates that model has been saved."""

    def __intit__(self, msg="The model could not be saved"):
        """Initialize message."""
        self.message = msg
