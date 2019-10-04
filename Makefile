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

# openshift deployment commands
oc_deploy_elasticsearch:
	oc process -f ./openshift/aiops_lad_core.elasticsearch.storage.yaml | oc apply -f -
	
oc_delete_elasticsearch:
	oc process -f ./openshift/aiops_lad_core.elasticsearch.storage.yaml | oc delete -f -

oc_deploy_sql_db:
	oc new-app centos/mysql-56-centos7 -e MYSQL_DATABASE=factstore -e MYSQL_PASSWORD=password -e MYSQL_USER=admin -e MYSQL_ROOT_PASSWORD=password

oc_delete_sql_db:
	oc delete all -l app=mysql-56-centos7

oc_deploy_factstore:
	oc process -f aiops_factstore.deployment.yaml | oc apply -f -

oc_delete_factstore:
	oc process -f aiops_factstore.deployment.yaml | oc delete -f -

