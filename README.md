# Anomaloy Detection in Logs - POC 

This repository contains the prototype for an application log Anomaly Detector which can be deployed either locally or on Openshift. It currently uses ElasticSearch as its source of data, gensim for Word2Vec log encoding, and a Self-Organizing map to analyze our streaming logs.

As with any Machine Learning pipeline there are two main portions of this repo: Training and Inference. Both stages of the ML pipeline can be run either locally or in OpenShift.

## Local Deployment

To run the Anomaly Detector locally, clone this repo and update the **env.sh** file with the relevent paramaters for your Elasticsearch instance, index and service as well as the appropriate training and testing pramaters. Documentation of each parameter can be found below as well as in the **env.sh** comments. Then on the command line type `. start.sh` to load the environment variables, train and save a model, then start watching for anomalies in your specified service.  



## Openshift Deployment

To run the above in Openshift, simply import the file **config.yaml** into your openshift project. This template file will prompt you for parameter inputs before deploying. Documentation for each parameter can be found below as well as within the **config.yaml** file. Once the application is created, it will start an s2i build from this git repository, and then deploy a pod that will first train and save a model, then start watch for anomalies in your specified service.  

## Paramaters

Both functions rely on correctly configuring below parameters, where the prefix LADT_ denotes Log Anomaly Detector Training (**trainer.py**) paramters and LADI_ denotes Log Anomaly Detector Inference (**infer.py**) parameters.

#### Training (trainer.py)

* LADT_MODEL_DIR = Name of persistant storage directory that models will be saved to
* LADT_ELASTICSEARCH_ENDPOINT = address to Elasticsearch endpoint
* LADT_MODEL = path to SOM map to update 
* LADT_INDEX = name of Elasticsearch index to pull logs from 
* LADT_TIME_SPAN = number of seconds from now that you would like to query Elasticsearch for training logs
* LADT_MAX_ENTRIES = limits the number of entries returned from Elasticsearch for the training query
* LADT_ITERS = number of training iterations of the SOM 
* LADT_SERVICE = name of Elasticsearch service to be monitored 
* LADT_TRAIN_LOG = Number of Inference iterations between retraining the model  



#### Inference (infer.py)

* LADI_ELASTICSEARCH_ENDPOINT = address to Elasticsearch endpoint for inference
* LADI_INDEX = path to SOM map to test against
* LADI_OUTDEX = name of index the anoamliy data will be pushed back to in Elasticsearch
* LADI_TIME_SPAN = number of seconds from now that you would like to query Elasticsearch for
* LADI_MAX_ENTRIES = limits the number of entries returned from Elasticsearch for the inference query
* LADI_SERVICE = name of Elasticsearch service to be monitored 
* LADI_THRESHOLD = float tunes the anomaly threshold based on the max value of the training set
* LADI_MAX_ANOMALIES = maximum number of anomalies allowed on each testing iteration


--------------------------------


## More Details


### Training 

**trainer.py** reads in log data from a specific service from an index at an Elasticsearch endpoint, parses the json data and converts it into a vector represntation using Word2Vec. It then trains a Self-Organizing Map on our current log data. This script then saves the W2V model as well as the trained SOM to disk to be used later by the inference script. **trainer.py** should be  re-run every so often to retrain our model with the most current data. It provides the option to either generate a new trained model or to update the existing model. 


### Inference

**infer.py** loads the models saved by the training script and (with default configuration) pulls the last minute of logs from a specific service at an Elasticsearch endpoint. It then updates the existing W2V models and converts the new data into vectors that can be fed into the Self-Organizing Map. The map will then prodice an anomaly score for each log


### Word2Vec

We are using Word2Vec in this application in order to vectorize the natural language elements of our log data. We have decided to use Word2Vec(https://en.wikipedia.org/wiki/Word2vec) because it has shown a great ability to convert text data into numerical vectors in such a way that much of their semantic meaning is retained. We have also decided to use the gensim package's verison of Word2Vec for this project. 


### SOM

SOM (Self_organizming map) is the learning algorithm used to help us quantify the anomalousness of our logs.  

SOM, or Kohonon maps, are a type of unsupervised learning algorithm that "produce a low-dimensional (typically two-dimensional), discretized representation of the input space of the training samples" (wikipedia: https://en.wikipedia.org/wiki/Self-organizing_map). The idea to use this type of algorithm for our log data was inspired by a talk by Will Benton (found here: https://www.youtube.com/watch?v=fhuoKe4li6E).

In short, we intialize a graph of some user-specified fixed dimensions, in our default case 24x24, where each node is an object of the same dimensions as our training data. We then iterate through each training example over the graph and find the node that is closest (here using L2 distance) to that trainng example. We then update the value of that node and the neighboring nodes. This process will generate a map that resembels the space of our training samples.

Once the map is trained, we can take a new example, measure its distance to each node on the map and determine how "close"/"similar" it is to our training data. This distance metric will be how we quantify the spectrum form normal to anomalous and how we generate our anomaly scores. 
