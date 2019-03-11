from pybloom import BloomFilter
from flask import Flask, request, render_template, jsonify
import pandas as pd
from fastparquet import write, ParquetFile
import os
import datetime

f = BloomFilter(capacity=1000, error_rate=0.001)
app = Flask(__name__, static_folder="static")


class FactStore:
    """
    FactStore:

    Service for feedback collection on accuracy of machine learning
    anomaly-detection

    """
    def __init__(self, feedback_metadata="metadata/feedback.parquet",
                 events_metadata="metadata/events.parquet"):
        """
        Has safe defaults and stores metadatafiles in metadata folder within
        :param feedback_metadata:
        :param events_metadata:
        """
        self.FEEDBACK_METAFILE = feedback_metadata
        self.EVENTS_METAFILE = events_metadata

    def write_event(self, predict_id, message, score, anomaly_status):
        """
        Service for storage of event metadata in parquet.

        :param id: predict Id where the anomaly details are stored
        :param message: the original message that triggered the anomaly
        :param score: the score that the algorithm set this anomaly
        :param anomaly_status: is this anomaly correct or false
        :return:
        """
        df = pd.DataFrame({'id': [predict_id],
                           'message': [message],
                           'score': [score],
                           'anomaly_status': [anomaly_status],
                           'date': [datetime.datetime.now()]})
        if os.path.exists(self.EVENTS_METAFILE):
            write(filename=self.EVENTS_METAFILE,
                  data=df,
                  append=True,
                  compression='GZIP')
        else:
            write(filename=self.EVENTS_METAFILE,
                  data=df,
                  compression='GZIP')
        print("Persisted ID: {}  recoreded in events_store".format(predict_id))

    def write_feedback(self, id, anomaly):
        """
        Service for storage of metadata in parquet.
         Also inserts id into bloom filter for quick lookup

        :param id: predict Id where the anomaly details are stored
        :param anomaly: is this anomaly correctly reported or false.
        :return:
        """
        if f.add(id) is False:
            df = pd.DataFrame({'id': [id],
                               'is_false_anomaly': [anomaly],
                               'date': [datetime.datetime.now()]})
            if os.path.exists(self.FEEDBACK_METAFILE):
                write(filename=self.FEEDBACK_METAFILE,
                      data=df,
                      append=True,
                      compression='GZIP')
            else:
                write(filename=self.FEEDBACK_METAFILE,
                      data=df,
                      compression='GZIP')
            print("Persisted ID: {} recorded in factstore ".format(id))
            return True
        print("Id {} already exists failed to sync ".format(id))
        return False

    def readall_feedback(self):
        """
        Service for querying datastore of current false anomalies
        :return:
        """
        pf = ParquetFile(self.FEEDBACK_METAFILE)
        df = pf.to_pandas()
        return df

    def is_not_anomaly(self, _id):
        return (_id in f)


@app.route("/")
def index():
    _id = request.args.get('lad_id')
    if _id is None:
        return render_template("index.html")
    return render_template("index.html", id=_id)


@app.route("/api/metadata", methods=['GET'])
def metadata():
    """ Service to provide list of false anomalies to be relabeled
        during ml training run"""
    fs = FactStore()
    df = fs.readall_feedback()
    return df.to_json(orient='records')


@app.route("/api/feedback", methods=['GET'])
def feedback():
    """ Feedback Service to provide user input on which
        false predictions this model provided."""
    _id = request.args.get('lad_id')
    anomaly = request.args.get('false_anomaly')
    if _id is None or anomaly is None:
        return "Must provide lad_id or anomaly parameter"
    print("id: {} ".format(_id))
    print("anomaly: {} ".format(anomaly))
    fs = FactStore()

    fs.write_feedback(_id, anomaly)
    return "success"


@app.route("/api/anomaly_event", methods=['POST'])
def false_anomaly():
    content = request.get_json()
    fs = FactStore()
    msg = content['message']
    # Checking bloom filter for if msg was reported
    anomaly_status = fs.is_not_anomaly(msg)
    # Tracking event in fact-store
    fs.write_event(content['predict_id'], content['message'],
                   content['score'], content['anomaly_status'])
    # Returning status if this anomaly is real anomaly_status== false
    return jsonify({"false_anomaly": anomaly_status})


if __name__ == "__main__":
    app.run(debug=True, port=5001, host="0.0.0.0")
