"""Storage package for utilizing source and sinks for ETL pipeline."""
from anomaly_detector.storage.es_storage import ESStorage
from anomaly_detector.storage.local_storage import LocalStorage
from anomaly_detector.storage.storage import Storage
from anomaly_detector.storage.storage_attribute import DefaultStorageAttribute, ESStorageAttribute

__all__ = ['ESStorage', 'LocalStorage', 'DefaultStorageAttribute', 'ESStorageAttribute', 'Storage']
