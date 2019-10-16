Metrics
=======

Visualizing the running ML system is important to measure success rate of the system. There is a dashboard
which you can import into your grafana installation and can be found here: https://bit.ly/2ppyFO0




Fact Store Metrics
------------------

Metrics for seeing the successful deployment of factstore. We may add more metrics in the future.

+-------------------------------+--------------------------------------------------------+-------------+
| Metric                        | Details                                                | Metric Type |
+===============================+========================================================+=============+
| aiops_human_feedback_count    | count of number of human feedback provided by customer | Counter     |
+-------------------------------+--------------------------------------------------------+-------------+
| aiops_human_feedback_error    | count of human feedback not able to write to db        | Counter     |
+-------------------------------+--------------------------------------------------------+-------------+


Core Metrics
------------

Metrics for visualizing the running ML job running and false positives found. We may add more metrics you will find
 updates here.

+------------------------------------+-----------------------------------------+-------------+
| Metric                             | Details                                 | Metric Type |
+====================================+=========================================+=============+
| aiops_lad_train_count              | count of training runs                  | Counter     |
+------------------------------------+-----------------------------------------+-------------+
| aiops_lad_inference_count          | count of inference runs                 | Counter     |
+------------------------------------+-----------------------------------------+-------------+
| aiops_lad_anomaly_count            | count of anomalies runs                 | Gauge       |
+------------------------------------+-----------------------------------------+-------------+
| aiops_lad_anomaly_avg_score        | avg anomaly score                       | Gauge       |
+------------------------------------+-----------------------------------------+-------------+
| aiops_lad_false_positive_count     | count of false positives processed runs | Counter     |
+------------------------------------+-----------------------------------------+-------------+
| aiops_hist                         | histogram of anomalies runs             | Histogram   |
+------------------------------------+-----------------------------------------+-------------+
| aiops_lad_threshold                | threshold of marker for anomaly         | Gauge       |
+------------------------------------+-----------------------------------------+-------------+