"""Storage Catalog class."""
from anomaly_detector.storage.kafka_storage import KafkaSink
from anomaly_detector.storage.local_storage import LocalStorageDataSource, LocalStorageDataSink
from anomaly_detector.storage.local_directory_storage import LocalDirectoryStorageDataSource
from anomaly_detector.storage.stdout_sink import StdoutSink
from anomaly_detector.storage.es_storage import ElasticSearchDataSink, ElasticSearchDataSource
import logging


class StorageCatalog(object):
    """Internal api and client should use storage proxy for data access.."""

    def __init__(self, config, storage_api):
        """Storage initialization logic."""
        self.config = config
        if storage_api in self._class_method_choices:
            self.storage_api = storage_api
        else:
            raise ValueError("Unsupported storage provider used {}".format(storage_api))

    @classmethod
    def _localdir_datasource_api(cls, config):
        """Local file storage api datasource construction."""
        logging.info("fetching localdir datasource")
        return LocalDirectoryStorageDataSource(configuration=config)

    @classmethod
    def _localfile_datasource_api(cls, config):
        """Local file storage api datasource construction."""
        logging.info("fetching localfile datasource")
        return LocalStorageDataSource(configuration=config)

    @classmethod
    def _localfile_datasink_api(cls, config):
        """Local file storage api datasink construction."""
        logging.info("save to localfile datasink")
        return LocalStorageDataSink(configuration=config)

    @classmethod
    def _elasticsearch_datasource_api(cls, config):
        """Local file storage api datasource construction."""
        logging.info("fetching elasticsearch datasource")
        return ElasticSearchDataSource(configuration=config)

    @classmethod
    def _elasticsearch_datasink_api(cls, config):
        """Local file storage api datasink construction."""
        logging.info("save to elasticsearch datasink")
        return ElasticSearchDataSink(configuration=config)

    @classmethod
    def _kafka_datasink_api(cls, config):
        """Kafka data sink."""
        logging.info("save kafka datasink")
        return KafkaSink(config=config)

    @classmethod
    def _stdout_datasink_api(cls, config):
        """Stdout data sink."""
        logging.info("save stdout datasink")
        return StdoutSink(config=config)

    _class_method_choices = {'local.sink': _localfile_datasink_api,
                             'local.source': _localfile_datasource_api,
                             'es.sink': _elasticsearch_datasink_api,
                             'es.source': _elasticsearch_datasource_api,
                             'kafka.sink': _kafka_datasink_api,
                             'localdir.source': _localdir_datasource_api,
                             'stdout.sink': _stdout_datasink_api}

    def get_storage_api(self):
        """Storage api."""
        return self._class_method_choices[self.storage_api].__get__(None, self.__class__)(self.config)
