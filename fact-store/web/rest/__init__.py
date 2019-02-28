from flask import Flask, request, render_template
import pandas as pd
from fastparquet import write, ParquetFile
import boto3
import os
import datetime

PARQUET_FILE_NAME = 'metadata/factstore.parquet'
app = Flask(__name__, static_folder="static")



@app.route("/")
def index():
    id = request.args.get('lad_id')
    if id is None:
        return render_template("index.html")
    return  render_template("index.html",id=id)


def persistMetadataToFactStore(id, anomaly):
    # TODO: Store results in parquet store
    df = pd.DataFrame({'id': [id], 'is_false_anomaly': [anomaly],'date': [datetime.datetime.now()]})
    if os.path.exists(PARQUET_FILE_NAME):
        write(filename=PARQUET_FILE_NAME, data=df, append=True, compression='GZIP')
    else:
        write(filename=PARQUET_FILE_NAME, data=df, compression='GZIP')
    print("Syncing factstore")
    # TODO: Uncomment below so you can test out S3 integration.
    #syncModel()



@app.route("/api/metadata", methods=['GET'])
def metadata():
    """ Service to provide list of false anomalies to be relabeled during ml training run"""
    pf = ParquetFile(PARQUET_FILE_NAME)
    df = pf.to_pandas()
    return df.to_json(orient='records')

@app.route("/api/feedback", methods=['GET'])
def feedback():
    """ Feedback Service to provide user input on which false predictions this model provided."""
    id = request.args.get('lad_id')
    anomaly = request.args.get('false_anomaly')
    if id is None or anomaly is None:
        return "Must provide lad_id or anomaly parameter"
    print("id: "+ id);
    print("anomaly: "+ anomaly);
    persistMetadataToFactStore(id,anomaly)
    return "success"


