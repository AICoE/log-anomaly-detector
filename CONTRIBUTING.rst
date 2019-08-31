

We like contributions and PR's you can contribute to this project at all skill levels. We have written this guide to allow anyone to be able to follow these steps and be able to build and run this project on their laptop. The following instructions provide details about how you would build, test and run this code.


Create a folder for your project

    `mkdir project_folder`
    
    `cd project_folder/`

Install virtualenv for installing all your dependencies in your sandbox.

	`pip3 install virtualenv`
    
	`python3 -m virtualenv venv`
    
	`source venv/bin/activate`

Fork the project and clone the repo

	`git clone https://github.com/<YOUR_GIT_ID>/log-anomaly-detector.git`

	`git remote add upstream https://github.com/aicoe/log-anomaly-detector.git`
	`cd log-anomaly-detector/`


Install pipenv to allow for dependencie installation via Pipfile

	`pip install pipenv`



Install all dependencies by running the following command

	`pipenv install --dev --deploy`



Run all tests

	`pipenv run python setup.py test --addopts -vs`



Running code linting tool. If you see a failure like this:

	`docker run -ti -v $(pwd):/app --workdir=/app coala/base coala --ci`
    
    
Running Fact Store
------------------

For example if your username is zak and password is password

        `export SQL_CONNECT="mysql+pymysql://zak:password@localhost/factstore"`


        `python app.py --metric-port 8081 ui`


Running log anomaly detector on sample data.
--------------------------------------------
.. warning::

  Make sure you delete the models directory: 
  `rm -rf logs/models/*`


`python app.py run --config-yaml .env_cmn_log_fmt_config.yaml --single-run True`



