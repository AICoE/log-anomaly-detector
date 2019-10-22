"""Stdout sink."""
import logging
from anomaly_detector.storage.storage_sink import StorageSink


class StdoutSink(StorageSink):
    """Standard output sink to allow us to help debug."""

    def __init__(self, config):
        """Initialize storage."""
        self.config = config

    def store_results(self, entries):
        """Sink stores results in system. We output logs to standard console of what is considered anomaly."""
        logging.info("You can click the following links to provide feedback to factstore")
        if self.config.FACT_STORE_URL:
            for entry in entries:
                try:
                    if entry.get('anomaly') is 1:
                        logging.info("{}?lad_id={}&is_anomaly={}&message={}".format(self.config.FACT_STORE_URL,
                                                                                    entry['predict_id'], "False",
                                                                                    entry['e_message']))
                except Exception as e:
                    logging.debug(e)
            logging.info("output logs {} in stdout.sink".format(len(entries)))
        else:
            logging.error("To use stdout.sink you must set FACT_STORE_URL config")
