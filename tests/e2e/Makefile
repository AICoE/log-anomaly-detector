.SILENT: help

help:
	echo "Use this make file to use pre-configured config files for fast use."
	echo "make [runtests | clean] ARGS "
	echo
	echo "ARGS:"
	echo "host		OCP host, format must be <host>:<port> e.g. localhost:8443"
	echo "auth		OCP Auth Token"
	echo "namespace OCP namespace to run tests in"

e2e-tests-run:
	sed -e 's/<host>/$(host)/g' -e 's/<auth_token>/$(auth)/g' -e 's/<namespace>/$(namespace)/g' configs/fulltest.yaml > config.yaml
	pipenv run pytest test_openshift_deployments.py --pytest_config=config.yaml

e2e-tests-clean:
	sed -e 's/<host>/$(host)/g' -e 's/<auth_token>/$(auth)/g' -e 's/<namespace>/$(namespace)/g' configs/cleanup.yaml > config.yaml
	pipenv run pytest test_openshift_deployments.py --pytest_config=config.yaml
