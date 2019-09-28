Use Case / Motivation
======================


Who likes reading logs? Can we automate identifying abnormal behaviour with machine learning? 



Why do we need it
-----------------

When  something goes wrong in an application there are 2 significant costs:

1. The time that it costs too debug the problem and fix the problem is expensive.

2. A temporary loss of service can both prevent transactions and can erode user confidence



Problems
--------

- Too much data for humans to process. 
- We think there is significant potential for machine learning to help automate this task.
- We think that you can use unsupervised machine learning to identify abnormal behavior.


What Are Logs Used For
----------------------

Databases:

- Produce transaction logs to track events that happen. 

Web analytics:

- May track user behavior or visits to provide web analytics or provide recommendations

Product Analytics:

- To find problems and for product improvements you may want to collect data about your product usage and also when your product crashes to be analyzed.

Root Cause Analysis:

- Often devops may have to dive through many logs to understand why an outage happened or what caused an error. We call this root cause analysis. Perhaps the most time consuming.



Near Term Goals
---------------

- Highlight which application logs are the most problematic the administrators should be alerted to take action. This can reduce outage time.

Far Term Goals
--------------
- Once we know what behavior is abnormal can we take action to remediate the issue? Or when we get warning signs can we take pre-emptive actions? This is a stretch goal in the horizon for the future of this project. But out of scope at this time.


