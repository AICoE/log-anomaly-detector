"""Feedback strategy for custom behaviour of false positive input."""
import types
import requests
import logging


class FeedbackStrategy():
    """Custom Feedback strategy for overwriting behaviour of application to provide configurable api."""

    def __init__(self, config, fn=None):
        """Initial setup of configuration and users can provide custom feedback_function to execute."""
        self.config = config
        if fn:
            self.execute = types.MethodType(fn, self)

    def execute(self):
        """Fetch false positive from datastore and add noise to training run."""
        logging.info("Fetching false positives from fact store")
        try:
            r = requests.get(url=self.config.FACT_STORE_URL + "/api/false_positive")
            data = r.json()
            false_positives = []
            for msg in data["feedback"]:
                noise = [{"message": msg}] * self.config.FREQ_NOISE
                false_positives.extend(noise)
            logging.info("Added noise {} messages ".format(len(false_positives)))
            return false_positives
        except Exception as ex:
            logging.error("Fact Store is either down or not functioning")
            return None
