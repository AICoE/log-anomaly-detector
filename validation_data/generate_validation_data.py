"""Generates filebased dataset for training."""
import json
import numpy as np
import random
import pickle
from elasticsearch2 import Elasticsearch
import os

ENDPOINT = os.environ["LAD_ENDPOINT"]
INDEX = os.environ["LAD_INDEX"]
SERVICE = os.environ["LAD_SERVICE"]

DEFALULT_QUERY = {
    "query": {"match": {"service": SERVICE}},
    "filter": {"range": {"@timestamp": {"gte": "now-2s", "lte": "now"}}},
    "sort": {"@timestamp": {"order": "desc"}},
    "size": 20,  # size is more critical than "terminate_after" to limit query size!!!
}


def get_data_from_es(endpoint, index, service, num=20, time=2, query=DEFALULT_QUERY):
    """Get data from elasticsearch using index name."""
    es = Elasticsearch(endpoint, timeout=30)
    query["size"] = num
    query["filter"]["range"]["@timestamp"]["gte"] = "now-" + str(time) + "s"
    query["query"]["match"]["service"] = service

    return es.search(index, body=json.dumps(query), request_timeout=500)


def create_anomlous_entires(string, entropy):
    """Take a string and randomly replaces characters with random characters."""
    string_length = len(string)

    if entropy > 1:
        raise ValueError("entropy should be a real valued number between 0 and 1")
    for i in range(round(string_length * entropy)):
        random_location = random.randint(0, string_length - 1)
        string = list(string)
        string[random_location] = chr(random.randint(65, 123))
        string = "".join(string)

    return string


def main():
    """Main method for loading in elasticsearch data."""
    random.seed(42)
    data = get_data_from_es(ENDPOINT, INDEX, SERVICE, num=80000, time=6000000)
    logs = data["hits"]["hits"]

    eighty_percent = int(round(len(logs) * 0.80))
    y = np.zeros(len(logs))
    anomaly_degrees = [0, 1]
    labels = [0, 1]

    data = []
    label = 0

    for i in range(0, eighty_percent):
        current_log = logs[i]["_source"]
        data.append({"message": current_log["message"].strip()})
        y[i] = labels[label]

    for i in range(eighty_percent, len(logs)):  # only the last 20% of the data will have anomlies.
        current_log = logs[i]["_source"]
        gate = random.randint(1, 100)

        if gate < 90:
            pass
        if gate >= 90:
            label = 1

        data.append({"message": create_anomlous_entires(current_log["message"].strip(), anomaly_degrees[label])})
        y[i] = labels[label]
        label = 0

    print(len(data), "logs and corresponding labels saved to disk as verification_data.json and labels.pkl")

    with open("verification_data.json", "w") as outfile:
        json.dump(data, outfile)

    with open("labels.pkl", "wb") as f:
        pickle.dump(y, f)
    len(logs)


if __name__ == "__main__":
    main()
