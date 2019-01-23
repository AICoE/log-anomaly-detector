#!/bin/sh
VERSION="0.1-rc2"
MAINTAINERS="Zak Hassan"
COMPONENT="log-anomaly-detection"

#cleaning up the image folder:

PUBLIC_IMAGE_NAME=quay.io/zmhassan/$COMPONENT:$VERSION
IMAGE_NAME=$COMPONENT:$VERSION

s2i build . docker.io/centos/python-36-centos7:latest $IMAGE_NAME

docker tag  $IMAGE_NAME $PUBLIC_IMAGE_NAME
docker push  $PUBLIC_IMAGE_NAME
