ui:
	pipenv run python app.py ui
run-with-factstore-local-full:
	pipenv run python app.py run --config-yaml .test_env_config_fact_store.yaml
run-with-factstore-local-train:
	pipenv run python app.py run --config-yaml .test_env_config_fact_store.yaml --job-type train
run-with-factstore-local-inference:
	pipenv run python app.py run --config-yaml .test_env_config_fact_store.yaml --job-type inference
run-with-local:
	pipenv run python app.py run --config-yaml .test_env_config.yaml --job-type train
test:
	pipenv run python setup.py test --addopts -vs

