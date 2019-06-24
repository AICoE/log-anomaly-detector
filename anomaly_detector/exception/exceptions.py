"""Fact Store Exception - When required env vars are not set we throw these exceptions."""


class FactStoreOffline(Exception):
    """Fact Store env var validator."""

    def __init__(self, msg="fact store url env var not set"):
        """Initialize message."""
        self.message = msg


class EmptyDataSetNotAllowed(ValueError):
    """Empty Dataset validator."""

    def __init__(self, msg="Reading from empty file or dataset streaming has no data."):
        """Initialize message."""
        self.message = msg
