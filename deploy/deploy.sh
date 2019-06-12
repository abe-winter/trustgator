#!/usr/bin/env bash
# deploy.sh -- deploy .lastbuild to kube

set -euo pipefail

PROJ=$(gcloud config get-value project)
IMG=us.gcr.io/$PROJ/tgtr-flask
THISDIR=$(dirname $0)
TAG=$(cat $THISDIR/../.lastbuild)

set -x
helm upgrade trustgator $THISDIR/trustgator --set image=$IMG:$TAG
