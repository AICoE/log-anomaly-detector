# Anomaloy Detection in Logs - POC 

This repository contains the prototype for a Log Anomaly Detector. It currently uses ElasticSearch as its source of data, gensim for log encoding, and Self-Organizing maps for analyzing logs. 

This repo has two main scripts **trainer.py** and ***infer.py***. 
* trainer.py trains our log analysis model and saves it to disk. 
* infer.py uses the trained model to analyis logs continually. 

**trainer.py*** takes 4 command line arguments: model, timespan (in seconds), max entries, and number of iterations. If you run, `python trainer.py model.sav, 600, 100000, 10000`. It will load a saved model if it exists, pull the last 10 minutes of data from service 'journal' from ES up to 100,000 records and will iterate over the SOM 10,000 times. It will then save the word2vec models, the SOM map, baseline meta_data about the training set, and a plot of the U-map to your working directory. It takes about 8 minutes to process 10 minutes (~15,000 logs) of data for one service.

**infer.py** currently takes no command line arguments, but is hard-coded to look at the last 60 seconds of logs, and load the info saved by trainer.py. To run this script simply use `python infer.py` from the command line. This script also has a 'while True' loop so that every minute it pulls the last minute of data and generates an anomaly score for each log until you manually shut it down. At each minute it will look at the 5 most anomalous logs and print their messages out if they are 3.5 times greater than the training data's standard deviation.
