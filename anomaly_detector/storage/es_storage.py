"""
"""

import datetime
from pandas.io.json import json_normalize
from elasticsearch2 import Elasticsearch, helpers
import json

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
        self.es = Elasticsearch(self.config.storage.ES_ENDPOINT, timeout=60, max_retries=2)

    def _prep_index_name(self, prefix):
        # appends the correct date to the index prefix
        now = datetime.datetime.now()
        date = now.strftime("%Y.%m.%d")
        index = prefix + date
        return index

    def retrieve(self, time_range: int, number_of_entires: int):
        """Retrieve data from ES."""
        index_in = self._prep_index_name(self.config.storage.ES_INPUT_INDEX)

        query = {'query': {'match': {'service': 'journal'}},
                 "filter": {"range": {"@timestamp": {"gte": "now-2s", "lte": "now"}}},
                 'sort': {'@timestamp': {'order': 'desc'}},
                 "size": 20
                 }

        _LOGGER.info("Reading in max %d log entries in last %d seconds from %s", number_of_entires, time_range, self.config.storage.ES_ENDPOINT)

        query['size'] = number_of_entires
        query['filter']['range']['@timestamp']['gte'] = 'now-%ds' % time_range
        query['query']['match']['service'] = self.config.storage.ES_SERVICE

        es_data = self.es.search(index_in, body=json.dumps(query))

        # only use _source sub-dict
        es_data = [x['_source'] for x in es_data['hits']['hits']]
        es_data_normalized = json_normalize(es_data)

        _LOGGER.info("%d logs loaded in from last %d seconds", len(es_data_normalized), time_range)

        self._preprocess(es_data_normalized)

        return es_data_normalized, es_data  # bad solution, this is how Entry objects could come in. 

    def store_results(self, data):
        """Store results back to ES."""
        index_out = self._prep_index_name(self.config.storage.ES_TARGET_INDEX)

        actions = [{"_index": index_out,
                    "_type": "log",
                    "_source": data[i]}
                   for i in range(len(data))]

        helpers.bulk(self.es, actions, chunk_size=int(len(data)/4)+1)


class ESConfiguration(Configuration):
    """Elasticsearch configuration."""

    # ElasticSearch endpoint URL
    ES_ENDPOINT = ""
    # ElasticSearch index name where results will be pushed to
    ES_TARGET_INDEX = ""
    # ElasticSearch index name where log entries will be pulled from
    ES_INPUT_INDEX = ""
    # Name of the service to be used in the ElasticSearch query
    ES_SERVICE = ""

    def __init__(self):
        """Initialize ES configuration."""
        self.load()
