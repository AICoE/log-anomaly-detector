"""
Log Anomaly Detector
"""

import sys
import logging
import os
import argparse
from anomaly_detector.anomaly_detector import AnomalyDetector
from anomaly_detector.config import Configuration
_LOGGER = logging.getLogger()
_LOGGER.setLevel(logging.INFO)

# create a logging format
FORMATTER = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

SH = logging.StreamHandler(sys.stdout)
SH.setFormatter(FORMATTER)
_LOGGER.addHandler(SH)

W2V_LOGGER = logging.getLogger('gensim.models')
W2V_LOGGER.setLevel(logging.ERROR)

CONFIGURATION_PREFIX = "LAD"


def _main():
    _LOGGER.info("Starting...")
    config = Configuration(CONFIGURATION_PREFIX)
    anomaly_detector = AnomalyDetector(config)

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", nargs='?', default="all")
    parser.add_argument("--modelstore", nargs='?')

    args = parser.parse_args()
    if args.mode == 'train' or os.getenv("LAD_MODE") == "train":
        _LOGGER.info("Performing training...")
        anomaly_detector.train()
    elif args.mode == 'inference' or os.getenv("LAD_MODE") == "inference":
        _LOGGER.info("Perform inference...")
        anomaly_detector.infer()
    elif args.mode == 'all':
        _LOGGER.info("Perform training and inference in loop...")
        anomaly_detector.run()

    _LOGGER.info("Job Complete")


if __name__ == "__main__":
    _main()
