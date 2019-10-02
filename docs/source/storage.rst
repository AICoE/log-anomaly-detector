Storage
=======

There are 2 storage backends implemented at the moment - ElasticSearch and local.

ElasticSearch
-------------
ES backend is pulling data from ElasticSearch instance. There are some assumptions made about the structure of the data and index names.

Index name is assumed to be in the format of index_name-YYYY.MM.DD, where the date is automatically appended based on current date - i.e. only provide index_name- prefix as a parameter
You index schema has to contain a service field which is used for filtering the input data
_source object in the index entry has to contain message field which then contains string representing the actual stored log message
Results are stored back into ElasticSearch as a copy of the input ElasticSearch index with the addition of two fields that help to identify logs as either anomalous or not for later review by users: anomaly, which is either 0 for false, or a 1 for true. And anomaly_score, a real valued number used to quantify the anomalousness of a log.

Local
-----
Local storage backend is able to read data from a file or standard input and write results back to a file or standard output.

Input data can be in a form of JSON (one entry per line) or plain text (simplified JSON object resembling the ES entry described above is constructed). We also support common logging format ["timestamp  severity    message"]


LocalDir
--------
This works the same as the local storage except this will let you read from a directory of logs which can either be json or common log. We support only files ending with '.log' or '.json'


.. code-block:: shell

   STORAGE_BACKEND: "es" # Reads logs from elasticsearch
   STORAGE_BACKEND: "local" # Reads logs from local file
   STORAGE_BACKEND: "localdir" # Reads logs from directory of files


.. note::

   You will need to set the configuration via cli to select which data provider you will use.

Extending Storage
-----------------

To extend storage with different storage systems:


.. literalinclude:: ../../anomaly_detector/adapters/base_storage_adapter.py





