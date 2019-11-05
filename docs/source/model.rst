Machine Learning Core
=====================

Language Encoding 
-----------------
This application requires that we take log messages, which are variable length character strings, and convert them into a fixed length vector representation that can be consumed by machine learning algorithms. There are a number of ways to do this, but here we use Word2Vec(https://en.wikipedia.org/wiki/Word2vec) as implemented by the gensim python package, which has shown a great ability to convert words into numerical vectors in such a way that much of their semantic meaning is retained. 



Word2Vec
--------

We are using Word2Vec in this application in order to vectorize the natural language elements of our log data. We have decided to use Word2Vec(https://en.wikipedia.org/wiki/Word2vec) because it has shown a great ability to convert text data into numerical vectors in such a way that much of their semantic meaning is retained. We have also decided to use the gensim package's verison of Word2Vec for this project.

SOM
---
SOM (self-organizing map) is the unsupervised learning algorithm used to help us quantify the anomalousness of our logs.

SOM, or Kohonon maps, are a type of unsupervised learning algorithm that "produce a low-dimensional (typically two-dimensional), discretized representation of the input space of the training samples" (wikipedia: https://en.wikipedia.org/wiki/Self-organizing_map). 

In short, we intialize a graph of some user-specified fixed dimensions, in our default case 24x24, where each node is an object of the same dimensions as our training data. We then iterate through each training example over the graph and find the node that is closest (here using L2 distance) to that training example. We then update the value of that node and the neighboring nodes. This process will generate a map that resembles the space of our training samples.

Once the map is trained, we can take a new example, measure its distance to each node on the map and determine how "close"/"similar" it is to our training data. This distance metric is how we quantify the spectrum from normal to anomalous and how we generate our anomaly scores.


Extending Model
---------------

If you desire to extend the machine learning models and would like to contribute your custom models you can extend:

.. literalinclude:: ../../anomaly_detector/adapters/base_model_adapter.py

