

We like contributions and PR's you can contribute to this project at all skill levels. We have written this guide to allow anyone to be able to follow these steps and be able to build and run this project on their laptop. The following instructions provide details about how you would build, test and run this code.


Create a folder for your project

     .. code-block:: shell

        $ mkdir project_folder
    
     .. code-block:: shell

        $ cd project_folder/

Install virtualenv for installing all your dependencies in your sandbox.

     .. code-block:: shell

        $ pip3 install virtualenv
    
     .. code-block:: shell

        $ python3 -m virtualenv venv
    
     .. code-block:: shell

        $ source venv/bin/activate

Fork the project and clone the repo


     .. code-block:: shell

        $ git clone https://github.com/<YOUR_GIT_ID>/log-anomaly-detector.git

     .. code-block:: shell

        $ cd log-anomaly-detector/

     .. code-block:: shell

        $ git remote add upstream https://github.com/aicoe/log-anomaly-detector.git


Install pipenv to allow for dependencie installation via Pipfile

     .. code-block:: shell

        $ pip install pipenv



Install all dependencies by running the following command

     .. code-block:: shell

        $ pipenv install --dev --deploy



Run all tests

     .. code-block:: shell

        $ pipenv run python setup.py test --addopts -vs



Running code linting tool. If you see a failure like this:

     .. code-block:: shell

        $ docker run -ti -v $(pwd):/app --workdir=/app coala/base coala --ci
    
    
Running Fact Store
------------------

For example if your username is zak and password is password

     .. code-block:: shell

        $ export SQL_CONNECT="mysql+pymysql://zak:password@localhost/factstore"
        $ python app.py --metric-port 8081 ui


Running log anomaly detector on sample data.
--------------------------------------------
.. warning::

  Make sure you delete the models directory: 
  rm -rf logs/models/*


.. code-block:: shell

        $ python app.py run --config-yaml .env_cmn_log_fmt_config.yaml --single-run True



