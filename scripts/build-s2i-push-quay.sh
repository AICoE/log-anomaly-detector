s2i build https://github.com/AICoE/log-anomaly-detector.git  docker.io/centos/python-36-centos7  log-anomaly-detector-image
docker tag log-anomaly-detector-image quay.io/aiops/log-anomaly-detector
docker push quay.io/aiops/log-anomaly-detector

