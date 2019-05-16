"""Fact Store Exception - When required env vars are not set we throw these exceptions."""


class factStoreEnvVarNotSetException(Exception):
    """Fact Store env var validator."""

    def __init__(self, msg="fact store url env var not set"):
        """Initialize message."""
        self.message = msg
