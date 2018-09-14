# Anomaly Detection in Logs

This repository contains the prototype for a Log Anomaly Detector (LAD) which can be deployed on Openshift. It supports multiple backends for data loading and uses Self-Organizing Maps to track differences and find anomalies in the log stream.

Internally it utilizes gensim for its Word2Vec implementation - used to encode the natural language portion of our logs, and an implementation of SOM, but it is possible to extend by other anomaly detection algorithms.

The execution flow containes of the two main portions (found in any ML application): training and inference.

## Local Development

You can install and run the application locally by running a standard Python installation using `setup.py`, which will also bring in all the dependencies to your machine.

```
python setup.py install
```

then start the application as (don't forget to replace  `...` will all the necessary environment variables)

```
LAD_STORAGE_BACKEND="es" ... python app.py
```

We recommend using containers and as we use source-to-image for deployments to OpenShift, we prefer to do the same for local development. For that you will need to download `s2i` binary from https://github.com/openshift/source-to-image/releases and install `docker`. To build an image with your application, run

```
s2i build --copy . centos/python-36-centos7 lad
```

To run the application, invoke a `docker run` command (don't forget to replace  `...` will all the necessary environment variables)

```
docker run -it --rm -e LAD_STORAGE_BACKEND="es" ... -v $PWD/:/opt/app-root/src/ -u 1000 lad
```


## Openshift Deployment


We provide an OpenShift template for the application, which you can import by

```
oc apply -f openshift/log-anomaly-detector.app.yaml
```

and then use OpenShift console to fill in the parameters, or do that from command line directly by calling


```
oc process -f openshift/log-anomaly-detector.app.yaml LAD_STORAGE_BACKEND="es" ... | oc apply -f -
```

This will deploy and trigger image build which in turn will deploy and start the application.


## Configuraiton

Configuration is currently done via environment variables. All the variables have prefix `LAD_` to distinguish them from the rest. 

Global application configuration options are defined and documented in `anomaly_detector/config.py`.

There are specific configuration variables for each storage backend, so consult configuration classes in `anomaly_detector/storage/` directory for those.

## More Details

### Training 

`anomaly_detector.train()` retrieves data from backend storage, converts it into vector representation using Gensim Word2Vec and stores the W2V model to disk. Next step is Self-Oragnizing Map training, once the model is trained, it is also stored to disk for furter use in `infer()`.

### Inference

`anomaly_detector.infer()` uses models stored on disk, loads new data from storage, updates W2V model to incorporate new tokens and get vectors for new data. Newly generated vectors are then fed into SOM and an anomaly score will be produced for each log entry. Threshold is used to decide whether the entry is an anomaly or not and results are fed back to the storage.

### Word2Vec

We are using Word2Vec in this application in order to vectorize the natural language elements of our log data. We have decided to use Word2Vec(https://en.wikipedia.org/wiki/Word2vec) because it has shown a great ability to convert text data into numerical vectors in such a way that much of their semantic meaning is retained. We have also decided to use the gensim package's verison of Word2Vec for this project. 


### SOM

SOM (Self_organizming map) is the unsupervised learning algorithm used to help us quantify the anomalousness of our logs.  

SOM, or Kohonon maps, are a type of unsupervised learning algorithm that "produce a low-dimensional (typically two-dimensional), discretized representation of the input space of the training samples" (wikipedia: https://en.wikipedia.org/wiki/Self-organizing_map). The idea to use this type of algorithm for our log data was inspired by a talk by Will Benton (found here: https://www.youtube.com/watch?v=fhuoKe4li6E).

In short, we intialize a graph of some user-specified fixed dimensions, in our default case 24x24, where each node is an object of the same dimensions as our training data. We then iterate through each training example over the graph and find the node that is closest (here using L2 distance) to that trainng example. We then update the value of that node and the neighboring nodes. This process will generate a map that resembels the space of our training samples.

Once the map is trained, we can take a new example, measure its distance to each node on the map and determine how "close"/"similar" it is to our training data. This distance metric is how we quantify the spectrum from normal to anomalous and how we generate our anomaly scores. 

### Storage

There are 2 storage backends implemented at the moment - ElasticSearch and local.

#### ElasticSearch

ES backend is pulling data from ElasticSearch instance. There are some assumptions made about the sturcture of the data and index names.

* Index name is assumed to be in the format of `index_name-YYYY.MM.DD`, where the date is automatically appended based on current date - i.e. only provide `index_name-` prefix as a parameter
* You index schema has to contain a `service` field which is used for filtering the input data
* `_source` object in the index entry has to contain `message` field which then contains string representing the actual stored log message

Results are stored back into ElasticSearch as a copy of the input ElasticSearch index with the addition of two fields that help to identify logs as either anomalous or not for later review by users: `anomaly`, which is either `0` for false, or a `1` for true. And `anomaly_score`, a real valued number used to quantify the anomalousness of a log.

#### Local

Local storage backend is able to read data from a file or standard input and write results back to a file or standard output.

Input data can be in a form of JSON (one entry per line) or plain text (simplified JSON object resembling the ES entry described above is constructed).
