"""Kafka Storage interface."""
import json
from kafka import KafkaProducer
from anomaly_detector.config import Configuration


class KafkaSink:
    """Kafka storage backend."""

    def __init__(self, config: Configuration):
        """Setup of kafka producer which will send messages to bootstrap server topic."""
        self.init_config(config)
        self.create_client()

    def init_config(self, config):
        """Initialize configurations for kafka communication."""
        self.bootstrap = config.KF_SINK_BOOTSTRAP_SERVER
        self.topic = config.KF_SINK_TOPIC
        self.cacert = config.KF_SINK_CACERT

    def create_client(self):
        """Initialize producer."""
        if not self.cacert:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap,
                                          api_version_auto_timeout_ms=30000)
        else:
            self.producer = KafkaProducer(bootstrap_servers=self.bootstrap,
                                          api_version_auto_timeout_ms=30000,
                                          security_protocol='SSL',
                                          ssl_cafile=self.cacert)

    def store_results(self, data):
        """Save data to Kafka."""
        dataset = json.dumps(data).encode('utf-8')
        self.producer.send(self.topic, dataset)

    def flush(self):
        """Important, especially if message size is small."""
        self.producer.flush()
