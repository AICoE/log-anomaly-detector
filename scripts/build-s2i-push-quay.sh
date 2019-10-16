VERSION="v0.1.0-beta.5"

s2i build https://github.com/AICoE/log-anomaly-detector.git  registry.access.redhat.com/ubi8/python-36  log-anomaly-detector-image
docker tag log-anomaly-detector-image quay.io/aiops/log-anomaly-detector:$VERSION
docker push quay.io/aiops/log-anomaly-detector:$VERSION

