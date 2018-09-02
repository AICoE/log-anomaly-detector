from anomaly_detector.anomaly_detector import AnomalyDetector
import os
import logging

from anomaly_detector.config import Configuration

CONFIGURATION_PREFIX = "LAD"

def main():
	config = Configuration(CONFIGURATION_PREFIX)
	anomaly_detector = AnomalyDetector(config)

	while True:
		if os.path.isfile(config.MODEL_PATH) and not config.TRAIN_UPDATE_MODEL:
			logging.info("Models already exists, skipping training")
		else:
			try:
				anomaly_detector.train()
			except Exception as e:
				logging.error(e)
				raise
		
		anomaly_detector.infer()

if __name__ == "__main__":
    main()
