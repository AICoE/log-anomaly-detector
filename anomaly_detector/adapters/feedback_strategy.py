"""Feedback strategy for custom behaviour of false positive input."""
import types
import requests
import logging


class FeedbackStrategy():
    """Custom Feedback strategy for overwriting behaviour of application to provide configurable api."""

    def __init__(self, config, func=None):
        """Initial setup of configuration and users can provide custom feedback_function to execute."""
        self.config = config
        self.uniq_items = set()
        if func:
            self.execute = types.MethodType(func, self)

    def execute(self):
        """Fetch false positive from datastore and add noise to training run."""
        logging.info("Fetching false positives from fact store")
        self.uniq_items = set()
        if self.config.FACT_STORE_URL:
            try:
                response = requests.get(url=self.config.FACT_STORE_URL + "/api/false_positive")
                result_data = response.json()
                false_positives = []
                for msg in result_data["feedback"]:
                    self.uniq_items.add(msg)
                    noise = [{"message": msg}] * self.config.FREQ_NOISE
                    false_positives.extend(noise)
                logging.info("Added noise {} messages ".format(len(false_positives)))
                return false_positives
            except Exception as ex:
                logging.error("Fact Store is either down or not functioning")
        return None
