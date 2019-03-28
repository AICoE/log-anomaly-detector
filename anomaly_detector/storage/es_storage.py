"""
"""

import datetime
import pandas
from pandas.io.json import json_normalize
from elasticsearch5 import Elasticsearch, helpers
import json
import os
import urllib3

from .storage import Storage
from ..config import Configuration

import logging

_LOGGER = logging.getLogger(__name__)


class ESStorage(Storage):
    """Elasticsearch storage backend."""

    NAME = "es"
    _MESSAGE_FIELD_NAME = "_source.message"

    def __init__(self, configuration):
        """Initialize Elasticsearch storage backend."""
        super(ESStorage, self).__init__(configuration)
        self.config.storage = ESConfiguration()
        self._connect()

    def _connect(self):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        if len(self.config.storage.ES_CERT_DIR) and os.path.isdir(self.config.storage.ES_CERT_DIR):
            _LOGGER.warn(
                "Using cert and key in %s for connection to %s (verify_certs=%s)."
                % (
                    self.config.storage.ES_CERT_DIR,
                    self.config.storage.ES_ENDPOINT,
                    self.config.storage.ES_VERIFY_CERTS,
                )
            )
            self.es = Elasticsearch(
                self.config.storage.ES_ENDPOINT,
                use_ssl=self.config.storage.ES_USE_SSL,
                verify_certs=self.config.storage.ES_VERIFY_CERTS,
                client_cert=os.path.join(self.config.storage.ES_CERT_DIR, "es.crt"),
                client_key=os.path.join(self.config.storage.ES_CERT_DIR, "es.key"),
                timeout=60,
                max_retries=2,
            )
        else:
            _LOGGER.warn("Conecting to ElasticSearch without authentication.")
            print(self.config.storage.ES_USE_SSL)
            self.es = Elasticsearch(
                self.config.storage.ES_ENDPOINT,
                use_ssl=self.config.storage.ES_USE_SSL,
                verify_certs=self.config.storage.ES_VERIFY_CERTS,
                timeout=60,
                max_retries=2,
            )

    def _prep_index_name(self, prefix):
        # appends the correct date to the index prefix
        now = datetime.datetime.now()
        date = now.strftime("%Y.%m.%d")
        index = prefix + date
        return index

    def retrieve(self, time_range: int, number_of_entires: int):
        """Retrieve data from ES."""
        index_in = self._prep_index_name(self.config.storage.ES_INPUT_INDEX)

        query = {
            "sort": {"@timestamp": {"order": "desc"}},
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"analyze_wildcard": True, "query": ""}},
                        {"range": {"@timestamp": {"gte": "now-900s", "lte": "now"}}},
                    ],
                    "must_not": [],
                }
            },
        }
        _LOGGER.info(
            "Reading in max %d log entries in last %d seconds from %s",
            number_of_entires,
            time_range,
            self.config.storage.ES_ENDPOINT,
        )

        query["size"] = number_of_entires
        query["query"]["bool"]["must"][1]["range"]["@timestamp"]["gte"] = "now-%ds" % time_range
        query["query"]["bool"]["must"][0]["query_string"]["query"] = self.config.storage.ES_QUERY

        es_data = self.es.search(index_in, body=json.dumps(query))
        if es_data["hits"]["total"] == 0:
            return pandas.DataFrame(), es_data
        # only use _source sub-dict
        es_data = [x["_source"] for x in es_data["hits"]["hits"]]
        es_data_normalized = pandas.DataFrame(json_normalize(es_data)["message"])

        _LOGGER.info("%d logs loaded in from last %d seconds", len(es_data_normalized), time_range)

        self._preprocess(es_data_normalized)

        return es_data_normalized, es_data  # bad solution, this is how Entry objects could come in.

    def store_results(self, data):
        """Store results back to ES."""
        index_out = self._prep_index_name(self.config.storage.ES_TARGET_INDEX)

        actions = [{"_index": index_out, "_type": "log", "_source": data[i]} for i in range(len(data))]

        helpers.bulk(self.es, actions, chunk_size=int(len(data) / 4) + 1)


class ESConfiguration(Configuration):
    """Elasticsearch configuration."""

    # ElasticSearch endpoint URL
    ES_ENDPOINT = ""
    # Path to a directory where cert and key (es.crt and es.key) are stored for authentication
    ES_CERT_DIR = ""
    # If True, connect using ssl
    ES_USE_SSL = True
    # If True, verify SSL certificates
    ES_VERIFY_CERTS = False
    # ElasticSearch index name where results will be pushed to
    ES_TARGET_INDEX = ""
    # ElasticSearch index name where log entries will be pulled from
    ES_INPUT_INDEX = ""
    # JSON representing a query passed to ElasticSearch to match the data
    ES_QUERY = ""

    def __init__(self):
        """Initialize ES configuration."""
        self.load()
