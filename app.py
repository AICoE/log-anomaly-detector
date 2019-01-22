"""
Log Anomaly Detector
"""

from anomaly_detector.anomaly_detector import AnomalyDetector
import sys
import logging
import os
from anomaly_detector.config import Configuration
import argparse
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

    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", nargs='?', default="all")
    parser.add_argument("--modelstore", nargs='?')

    args = parser.parse_args()
    # Allow users to pick storage location we may want to
    # store our models in google cloud storage or azure instead of s3 in the future
    if args.modelstore=="s3" or os.getenv("MODEL_STORE")== "s3":
        _LOGGER.info("Model will be stored in s3")
        anomaly_detector.config.MODEL_STORE="s3"

    if args.mode == 'train' or os.getenv("MODE") == "train":
        _LOGGER.info ("Performing training...")
        anomaly_detector.train()
    elif args.mode == 'inference' or os.getenv("MODE") == "inference":
        _LOGGER.info("Perform inference...")
        anomaly_detector.infer()
    elif args.mode == 'all':
        _LOGGER.info("Perform training and inference in loop...")
        anomaly_detector.run()

    _LOGGER.info("Job Complete")


if __name__ == "__main__":
    _main()
