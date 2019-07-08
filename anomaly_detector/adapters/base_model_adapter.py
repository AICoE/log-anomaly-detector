"""Base Model Adaptor Class - As we try different models and developers can contribute their custom code."""

from abc import ABCMeta, abstractmethod


class BaseModelAdapter(metaclass=ABCMeta):
    """Base class for custom models."""

    @abstractmethod
    def train(self):
        """Train ml models."""
        raise NotImplementedError("Please implement the <train method>")

    @abstractmethod
    def predict(self):
        """Infer ml models."""
        raise NotImplementedError("Please implement the <infer method>")
