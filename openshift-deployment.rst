
Openshift Deployment
=====================


We provide an OpenShift template for the application, which you can import by

.. code-block::

        oc apply -f openshift/log-anomaly-detector.app.yaml

To install fact_store run:
Note: Make sure you set `FACT_STORE_URL` env var or factstore will be ignored


.. code-block::

        oc apply -f openshift/openshift/factstore.app.yaml

and then use OpenShift console to fill in the parameters, or do that from command line directly by calling


.. code-block::

        oc process -f openshift/log-anomaly-detector.app.yaml LAD_STORAGE_BACKEND="es" ... | oc apply -f -


This will deploy and trigger image build which in turn will deploy and start the application.






