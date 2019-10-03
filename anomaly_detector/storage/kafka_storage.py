"""Kafka Storage interface."""
import json
from kafka import KafkaProducer
from anomaly_detector.storage.storage_sink import StorageSink


class KafkaSink(StorageSink):
    """Kafka storage backend."""

    NAME = "kafka.sink"

    def __init__(self, config):
        """Setup of kafka producer which will send messages to bootstrap server topic."""
        self.bootstrap = config.KF_BOOTSTRAP_SERVER
        self.topic = config.KF_TOPIC
        self.cacert = config.KF_CACERT
        self.security_protocol = config.KF_SECURITY_PROTOCOL
        self.create_client()

    def create_client(self):
        """Initialize producer."""
        self.producer = KafkaProducer(bootstrap_servers=self.bootstrap,
                                      api_version_auto_timeout_ms=30000,
                                      security_protocol=self.security_protocol,
                                      ssl_cafile=self.cacert)

    def store_results(self, data):
        """Save data to Kafka."""
        dataset = json.dumps(data).encode('utf-8')
        self.producer.send(self.topic, dataset)

    def flush(self):
        """Important, especially if message size is small."""
        self.producer.flush()
