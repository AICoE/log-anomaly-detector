#!/usr/bin/env bash

datasource_name=prometheus

protocol=http://

datasource_payload="$( mktemp )"
cat <<EOF >"${datasource_payload}"
{
"name": "${datasource_name}",
"type": "prometheus",
"isDefault": true,
"typeLogoUrl": "",
"access": "proxy",
"url": "http://$( oc get route lad-prometheus-route -o jsonpath='{.spec.host}' )",
"basicAuth": false,
"withCredentials": false
}
EOF

## Data Source
# setup grafana data source
grafana_host="${protocol}$( oc get route lad-grafana-route -o jsonpath='{.spec.host}' )"

# wait for grafana api to be ready
until $(curl --output /dev/null --silent --head --fail "${grafana_host}/api/datasources" -u admin:admin); do
    printf 'Waiting for grafana deployment...\n'
    sleep 5
done

curl -H "Content-Type: application/json" -u admin:admin "${grafana_host}/api/datasources" -X POST -d "@${datasource_payload}"

## Dashboards
dashboard_json="$(cat ./openshift/metrics/grafana_dashboards/log_anomaly_detector_dashboard.json)"

dashboard_payload="$( mktemp )"

cat <<EOF >"${dashboard_payload}"
{
  "dashboard": ${dashboard_json}
}
EOF

curl  -H "Content-Type: application/json" -u admin:admin "${grafana_host}/api/dashboards/db" -X POST -d "@${dashboard_payload}"
