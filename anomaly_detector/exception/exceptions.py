"""Exceptions for the log anomaly detector."""


class FactStoreEnvVarNotSetException(Exception):
    """Fact Store env var validator."""

    def __init__(self, msg="fact store url env var not set"):
        """Initialize message."""
        self.message = msg


class ModelLoadException(Exception):
    """Validates that model has been loaded."""

    def __init__(self, msg="There is no existing model to load"):
        """Initialize message."""
        self.message = msg


class ModelSaveException(Exception):
    """Validates that model has been saved."""

    def __init__(self, msg="The model could not be saved"):
        """Initialize message."""
        self.message = msg


class FileFormatNotSupported(Exception):
    """Validates that fileformat is supported."""

    def __init__(self, msg="File format not supported"):
        """Initialize message."""
        self.message = msg


class EmptyDataSetException(Exception):
    """Validates there is empty dataset returned from ingest."""

    def __init__(self, msg="Empty dataset returned from ingest"):
        """Initialize message."""
        self.message = msg
