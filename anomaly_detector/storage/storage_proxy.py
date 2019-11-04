"""Storage Proxy."""
from anomaly_detector.config import Configuration
from anomaly_detector.storage.storage_catalog import StorageCatalog
from anomaly_detector.storage.storage_source import StorageSource
from anomaly_detector.storage.storage_sink import StorageSink


class StorageProxy(StorageSource, StorageSink):
    """Storage Proxy for facilitating communication with backend."""

    SUFFIX_SOURCE = ".source"
    SUFFIX_SINK = ".sink"

    def __init__(self, config: Configuration):
        """Create storage data source and sinks to talk to storage backend."""
        super().__init__(config)
        self.source = StorageCatalog(config=config,
                                     storage_api=config.STORAGE_DATASOURCE + self.SUFFIX_SOURCE).get_storage_api()
        self.sink = StorageCatalog(config=config,
                                   storage_api=config.STORAGE_DATASINK + self.SUFFIX_SINK).get_storage_api()

    def retrieve(self, storage_attribute):
        """Retrieve data from backend storage."""
        return self.source.retrieve(storage_attribute)

    def store_results(self, entries):
        """Store data into backend storage."""
        self.sink.store_results(entries)
