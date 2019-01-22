#!/bin/sh
VERSION="0.1-rc1"
MAINTAINERS="Zak Hassan"
COMPONENT="anomaly-detection-training"

#cleaning up the image folder:

DKR_HUB_NAME=quay.io/zmhassan/anomaly-detection-training:$VERSION
IMAGE_NAME=anomaly-detector-train:$VERSION

s2i build . docker.io/centos/python-36-centos7:latest $IMAGE_NAME

docker tag  $IMAGE_NAME $DKR_HUB_NAME
docker push  $DKR_HUB_NAME
