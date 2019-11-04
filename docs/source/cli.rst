CLI Documentation
=================

Description
-----------
The log-anomaly-detector command line tool to detect abnormal events logs using machine learning

Example
-------

.. code-block:: shell

   log-anomaly-detector [main-options] <command> <subcommand> [subcommand-options] [parameters]

This example above for each command shows its parameters and their usage. Optional parameters are shown in square brackets.

Main options
------------
Perform machine learning model generation with input log data.


    --metric-port (int)

Use this option to override the port that prometheus exposes metrics

RUN command
-----------

Perform machine learning model generation with input log data.


RUN command options
-------------------


    --config-yaml (string)

Select path to read configmap to overwrite default configuration for the application


    --tracing-enabled (boolean)

Provides ability to expose tracing information of ml jobs running underneath.


    --single-run (boolean)

By default the system will train and then perform inference. Then repeat.
If you would like to run the job once then you can set this property to True.


    --job-type (string)


Select what type of job to run. (Defaults to run both train and inference)
- train
- inference
- all (default)





UI command
----------


Run fact store ui and connect to database


UI command options
------------------


    --debug (boolean)

Sets flask in debug mode to true


    --port (int)

Select the port number you would like to run the web ui



Example Usage:
--------------


.. code-block:: shell

   log-anomaly-detector run --config-yaml config_files/.env_cmn_log_fmt_config.yaml --single-run True




.. code-block:: shell

   export SQL_CONNECT="mysql+pymysql://{USERNAME}:{PASSWORD}@localhost/factstore"
   export CUSTOMER_ID="test1"
   log-anomaly-detector ui --port 8080 --debug True


.. note::

    We need to set the environment variables SQL_CONNECT and we can choose a different connection string.
    See https://docs.sqlalchemy.org/en/latest/dialects/

