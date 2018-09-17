"""
Log Anomaly Detector
"""

from anomaly_detector.anomaly_detector import AnomalyDetector
import sys
import logging

from anomaly_detector.config import Configuration

_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(formatter)
_LOGGER.addHandler(sh)

w2v_logger = logging.getLogger('gensim.models')
w2v_logger.setLevel(logging.ERROR)

CONFIGURATION_PREFIX = "LAD"


def _main():
    _LOGGER.info("Starting...")
    config = Configuration(CONFIGURATION_PREFIX)
    anomaly_detector = AnomalyDetector(config)
    anomaly_detector.run()


if __name__ == "__main__":
    _main()
