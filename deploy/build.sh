#!/usr/bin/env bash
# build.sh -- build / upload docker image and set .lastbuild

set -euo pipefail

SHA=`git rev-parse HEAD`
TAG=${SHA:0:10}
PROJ=$(gcloud config get-value project)
IMG=us.gcr.io/$PROJ/tgtr-flask
THISDIR=$(dirname $0)

docker build $THISDIR/.. -t $IMG:$TAG
docker tag $IMG:$TAG $IMG:latest
docker push $IMG:$TAG
docker push $IMG:latest

echo $TAG > $THISDIR/../.lastbuild
