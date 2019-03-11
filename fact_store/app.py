from pybloom import BloomFilter
from flask import Flask, request, render_template
import pandas as pd
from fastparquet import write, ParquetFile
import os
import datetime
f = BloomFilter(capacity=1000, error_rate=0.001)
app = Flask(__name__, static_folder="static")


class FactStore:
    """
    FactStore:

    Service for feedback collection on accuracy of machine learning anomaly-detection

    """
    def __init__(self, parquet_file_name="metadata/parquet"):
        """ For those interested in overwriting the path that factstore is stored"""
        self.PARQUET_FILE_NAME = parquet_file_name


    def write(self, id, anomaly):
        """
        Service for storage of metadata in parquet. Also inserts id into bloom filter
        for quick lookup

        :param id: ElasticSearch Id where the anomaly details are stored
        :param anomaly: is this anomaly correctly reported or false.
        :return:
        """
        if (f.add(id) == False):
            df = pd.DataFrame({'id': [id], 'is_false_anomaly': [anomaly], 'date': [datetime.datetime.now()]})
            if os.path.exists(self.PARQUET_FILE_NAME):
                write(filename=self.PARQUET_FILE_NAME, data=df, append=True, compression='GZIP')
            else:
                write(filename=self.PARQUET_FILE_NAME, data=df, compression='GZIP')
            print("Persisted ID: {} and persisted record ".format(id))
            return True
        print("Id {} already exists failed to sync ".format(id))
        return False

    def readall(self):
        """
        Service for querying datastore of current false anomalies
        :return:
        """
        pf = ParquetFile(self.PARQUET_FILE_NAME)
        df = pf.to_pandas()
        return df

    def isduplicate(self, _id):
        return (f in _id)

@app.route("/")
def index():
    _id = request.args.get('lad_id')
    if _id is None:
        return render_template("index.html")
    return render_template("index.html",id=_id)

@app.route("/api/metadata", methods = ['GET'])
def metadata():
    """ Service to provide list of false anomalies to be relabeled during ml training run"""
    fs=FactStore()
    df = fs.readall()
    return df.to_json(orient='records')

@app.route("/api/feedback", methods = ['GET'])
def feedback():
    """ Feedback Service to provide user input on which false predictions this model provided."""
    _id = request.args.get('lad_id')
    anomaly = request.args.get('false_anomaly')
    if _id is None or anomaly is None:
        return "Must provide lad_id or anomaly parameter"
    print("id: {} ".format(_id))
    print("anomaly: {} ".format(anomaly))
    fs = FactStore()

    fs.write(_id, anomaly)
    return "success"


if __name__ == "__main__":
    app.run(debug=True, port=5001,host="0.0.0.0")
