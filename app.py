from anomaly_detector.anomaly_detector import AnomalyDetector
import os
import logging
import time

from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"

def main():
	config = Configuration(CONFIGURATION_PREFIX)
	anomaly_detector = AnomalyDetector(config)
	anomaly_detector.run()

if __name__ == "__main__":
    main()
