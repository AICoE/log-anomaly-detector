# Anomaly Detection in Logs

This repository contains the prototype for a Log Anomaly Detector (LAD) which can be deployed on Openshift. It supports multiple backends for data loading and uses Self-Organizing Maps to track differences and find anomalies in the log stream.

This application leverages both a Word2Vec implementation and a self organizing map to address this unsupervised natural language learning problem. We also have a user feedback subsystem, called Fact-Store, which maintains false positives flagged by users. This allows for the system to better learn how to avoid false positives in the future.

Internally it utilizes gensim for its Word2Vec implementation - used to encode the natural language portion of our logs, and an implementation of SOM, but it is possible to extend by other anomaly detection algorithms.

The execution flow contain's the two main portions (found in any ML application): training and inference.

## Use Case

The use case for this system is to assist in root cause analysis of logs. Instead of developers having to go through many lines of logs this system will flag the log lines that are anomalies that need to be looked at. We also bundle a secondary subsystem called a fact_store which will allow for human feedback on accuracy of model prediction by disabling false anomalies that where reported from notifying users.

## Language Encoding
This application requires that we take log messages, which are variable length character strings, and convert them into a fixed length vector representation that can be consumed by machine learning algorithms. There are a number of ways to do this, but here we use Word2Vec(https://en.wikipedia.org/wiki/Word2vec) as implemented by the gensim python package, which has shown a great ability to convert words into numerical vectors in such a way that much of their semantic meaning is retained.

## Configurations



You have 2 options when configuring the application.

1. Environment variables
2. Yaml

| Config Field            | Defaults                                                                                                                                                                                         | Description                                                                                                                                                                                                                                                                                                                                               |
|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FACT_STORE_EVENTS_URL   | “”                                                                                                                                                                                               | Sends events to fact-store                                                                                                                                                                                                                                                                                                                                |
| STORAGE_BACKEND         | ‘Local’{REQUIRED}Scorpio run --job-type train --data-source s3:// Scorpio run --job-type train --data-source kafka:// Scorpio run --job-type train --data-source file:// Consider removing this… | The location where data is stored                                                                                                                                                                                                                                                                                                                         |
| MODEL_DIR               | ‘./models/’’{OPTIONAL}                                                                                                                                                                           | Dictates the name of the folder used to store models generated. Useful if a user, doesn’t want to overwrite existing models.                                                                                                                                                                                                                              |
| MODEL_FILE              | {OPTIONAL} Defaults are SOMModel, W2VModel                                                                                                                                                       | Name of file where models are stored                                                                                                                                                                                                                                                                                                                      |
| W2V_MODEL_PATH          | {OPTIONAL}                                                                                                                                                                                       | File that is used for the word 2 vec model filename                                                                                                                                                                                                                                                                                                       |
| TRAIN_TIME_SPAN         | Default: 900                                                                                                                                                                                     | Amount of time in seconds that you pulled the logs from elasticsearch. This parameter allows users to decide the time window from now to TRAIN_TIME_SPAN for which batch inference will run.                                                                                                                                                              |
| TRAIN_MAX_ENTRIES       | Default: 30000                                                                                                                                                                                   | Maximum number of log messages read in from ElasticSearch during training                                                                                                                                                                                                                                                                                 |
| TRAIN_ITERATIONS        | Default: Training Data Batch Size                                                                                                                                                                | Parameter used to train the SOM model. Defines the number of training examples used to train the model                                                                                                                                                                                                                                                    |
| TRAIN_UPDATE_MODEL      | Defaults: False {OPTIONAL if you’ve done your training and you just want inference}                                                                                                              | If set to True, a pre-existing model is loaded for re-training. Otherwise, a new model is initialized.                                                                                                                                                                                                                                                    |
| TRAIN_WINDOW            | Default: 5                                                                                                                                                                                       | [HYPER_PARAMETER] This is a hyper parameter used by the Word2Vec to dictate the number of words behind and in front of the target word during training.,Users may want to tweek this parameter.                                                                                                                                                           |
| TRAIN_VECTOR_LENGTH     | Default: 25                                                                                                                                                                                      | [HYPER_PARAMETER] This is a hyper-parameter used by the,word2vec implementation to dictate the length of the feature vector generated from the log data for further processing by the SOM anomaly detection. Optimal feature length often can’t be known a priori,so users may want to tune this parameter based on their specific data set and use-case. |
| PARALLELISM             | Default: 2                                                                                                                                                                                       | Used to past through to SOMPy package. Number of jobs that can be parallelized                                                                                                                                                                                                                                                                            |
| INFER_ANOMALY_THRESHOLD | Default: 3.1                                                                                                                                                                                     | This value dictates how many standard deviations away from the mean a particular log anomaly value has to be before it will be classified as an anomaly.,If a user would like their system to be more strict they should increase this value. A value of 0 will classify all entries as anomalies.                                                        |
| INFER_TIME_SPAN         | Default: 60 seconds                                                                                                                                                                              | The time in seconds that each inference batch represents. A value of 60 will pull the last 60 seconds of logs into the system for inference.                                                                                                                                                                                                              |
| INFER_LOOPS             | Default: 10                                                                                                                                                                                      | Number of inference steps before retraining.                                                                                                                                                                                                                                                                                                              |
| INFER_MAX_ENTRIES       | Default: 78862                                                                                                                                                                                   | Maximum number of log messages read in from ElasticSearch during inference                                                                                                                                                                                                                                                                                |
| LS_INPUT_PATH           | None                                                                                                                                                                                             | Input data path. If your pulling data from elasticsearch then we accept urls. This is the path where log data is pulled in.                                                                                                                                                                                                                               |
| LS_OUTPUT_PATH          | None                                                                                                                                                                                             | Output data path. If your pulling data from elasticsearch then we accept urls. This is the path where log data is pulled in.                                                                                                                                                                                                                              |
| SQL_CONNECT             | sqlite://tmp/test.db                                                                                                                                                                             | Used to connect fact_store ui to database to store metadata. Not if you are running in openshift you can deploy mysql as a durable storage for that see mysql section.                                                                                                                                                                                    |


If you are testing locally you can do the following:

- Environment variables are loaded from `.env`. `pipenv` will load these automatically. So make sure you execute everything via `pipenv run` or from a `pipenv shell`.

Configuration is currently done via environment variables. All the variables have prefix `LAD_` to distinguish them from the rest.

Global application configuration options are defined and documented in `anomaly_detector/config.py`.

There are specific configuration variables for each storage backend, so consult configuration classes in `anomaly_detector/storage/` directory for those.


```
cp .env.example .env`
```

You may also use a config yaml file by passing it in via the following command:
```
python app.py run  --config-yaml env_config.yaml
```

When using the CLI you can run it outside of kubernetes and pass in `--job-type` which will default to train and inference. If you would like to override that in openshift you can passing a command and also arguments to that command. Template will be provided to utilize this.


You can install and run the application locally by running a standard Python installation using `pipenv`, which will also bring in all the dependencies to your machine.

```
pipenv install --dev
```


then start the application via

```
pipenv run python app.py run --job-type train --config-yaml env_config.yaml
```

Steps to run locally:

Note: Make sure you set SQL_CONNECT env var to mysql. Preload it with data if you want. Then start fact_store:

```
python app.py run ui
```
Run training and inference

```
python app.py run --config-yaml .test_env_config_fact_store.yaml
```

## Feedback Loop And Noise:

The purpose is that we want to increase the occurrences of log lines that are false positives so the SOM model will give it a lower score thus not triggering an false anomaly prediction. We have an additional check in place. I guess we can probably measure how well this performs overtime. W2v and SOM ML Models should learn overtime. This is an example of when we increase the log frequency notice the score decrease: 

**Note:** `FREQ_NOISE` by increasing the frequency of a log line it will result 
in a reduced anomaly score not breaking the threshold. 

For example:

 ![Anomaly_False_Positive](https://user-images.githubusercontent.com/1269759/58996555-b3b88700-87c6-11e9-8e0d-0bf947e02699.png)

## Source To Image And Containers

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
To install fact_store run:
Note: Make sure you set `FACT_STORE_URL` env var or factstore will be ignored

```
oc apply -f openshift/openshift/factstore.app.yaml
```
and then use OpenShift console to fill in the parameters, or do that from command line directly by calling


```
oc process -f openshift/log-anomaly-detector.app.yaml LAD_STORAGE_BACKEND="es" ... | oc apply -f -
```

This will deploy and trigger image build which in turn will deploy and start the application.



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
