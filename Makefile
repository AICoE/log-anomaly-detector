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

# namespace/project where all the deployments will be made
NAMESPACE=lad
# route for the Factstore deployed
FACTSTORE_ROUTE="http://LAD.FACTSTORE.URL.ENTER.HERE.com/"
# mailing server used by elastalerts to send anomaly alerts
SMTP_SERVER_URL="my.mailing.server.url"

# openshift deployment commands
oc_deploy_elasticsearch:
	oc process -f ./openshift/aiops_lad_core.elasticsearch.storage.yaml | oc apply -f - -n ${NAMESPACE}

oc_delete_elasticsearch:
	oc process -f ./openshift/aiops_lad_core.elasticsearch.storage.yaml | oc delete -f - -n ${NAMESPACE}

oc_deploy_sql_db:
	oc new-app centos/mysql-56-centos7 -e MYSQL_DATABASE=factstore -e MYSQL_PASSWORD=password -e MYSQL_USER=admin -e MYSQL_ROOT_PASSWORD=password -n ${NAMESPACE}

oc_delete_sql_db:
	oc delete all -l app=mysql-56-centos7 -n ${NAMESPACE}

oc_deploy_factstore:
	oc process -f ./openshift/aiops_factstore.deployment.yaml | oc apply -f - -n ${NAMESPACE}

oc_delete_factstore:
	oc process -f ./openshift/aiops_factstore.deployment.yaml | oc delete -f - -n ${NAMESPACE}

oc_deploy_lad:
	oc process -f ./openshift/log-anomaly-detector-minishift.yaml -p FACT_STORE_URL=${FACTSTORE_ROUTE} -p ES_ENDPOINT="lad-elasticsearch-service.${NAMESPACE}.svc:9200" | oc apply -f - -n ${NAMESPACE}

oc_delete_lad:
	oc process -f ./openshift/log-anomaly-detector-minishift.yaml -p FACT_STORE_URL=${FACTSTORE_ROUTE} -p ES_ENDPOINT="lad-elasticsearch-service.${NAMESPACE}.svc:9200"| oc delete -f - -n ${NAMESPACE}

oc_deploy_demo_app:
	oc process -f https://raw.githubusercontent.com/AICoE/anomaly-detection-demo-app/master/openshift/ad_demo.yaml | oc apply -f - -n ${NAMESPACE}

oc_build_elastalert_image:
	oc process -f ./openshift/elastalert/lad-elastalert-buildconfig.yaml | oc apply -f - -n ${NAMESPACE}

oc_delete_elastalert_image:
	oc process -f ./openshift/elastalert/lad-elastalert-buildconfig.yaml | oc delete -f - -n ${NAMESPACE}

oc_deploy_elastalert:
	oc process -f ./openshift/elastalert/lad-elastalert-deployment.yaml -p FACTSTORE_URL=${FACTSTORE_ROUTE} -p SMTP_SERVER=${SMTP_SERVER_URL}| oc apply -f - -n ${NAMESPACE}

oc_delete_elastalert:
	oc process -f ./openshift/elastalert/lad-elastalert-deployment.yaml -p FACTSTORE_URL=${FACTSTORE_ROUTE} -p SMTP_SERVER=${SMTP_SERVER_URL}| oc delete -f - -n ${NAMESPACE}

oc_deploy_prometheus:
	oc process -f ./openshift/metrics/prometheus.yaml -p TARGET_HOSTS="anomaly-detection-demo.${NAMESPACE}.svc:8088, log-anomaly-detector-demo-svc.${NAMESPACE}.svc:8080" | oc apply -f - -n ${NAMESPACE}

oc_delete_prometheus:
	oc process -f ./openshift/metrics/prometheus.yaml -p TARGET_HOSTS="anomaly-detection-demo.${NAMESPACE}.svc:8088, log-anomaly-detector-demo-svc.${NAMESPACE}.svc:8080" | oc delete -f - -n ${NAMESPACE}

oc_deploy_grafana:
	oc process -f ./openshift/metrics/grafana.yaml | oc apply -f - -n ${NAMESPACE}
	./openshift/metrics/setup_grafana.sh

oc_delete_grafana:
	oc process -f ./openshift/metrics/grafana.yaml | oc delete -f - -n ${NAMESPACE}

echo_message:
	echo "Please update the vars FACTSTORE_ROUTE and SMTP_SERVER_URL in this Makefile"

# minishift start
minishift_start:
	# these commands should run before a vm is created
	minishift config set --global memory 8192 # give the cluster about 8 gigs of memory
	minishift config set --global cpus 6 # and 6 vcpus

	# start the cluster this will take some time
	minishift start

oc_deploy_demo_prereqs: oc_deploy_sql_db oc_deploy_elasticsearch oc_deploy_factstore oc_deploy_demo_app oc_build_elastalert_image echo_message

oc_deploy_demo_monitoring: oc_deploy_prometheus oc_deploy_grafana
