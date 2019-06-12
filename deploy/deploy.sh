#!/usr/bin/env bash
# deploy.sh -- deploy .lastbuild to kube

set -euo pipefail

PROJ=$(gcloud config get-value project)
IMG=us.gcr.io/$PROJ/tgtr-flask
TAG=$(cat .lastbuild)
THISDIR=$(dirname $0)

set -x
helm upgrade trustgator $THISDIR/trustgator -f $THISDIR/trustgator/values_gke_headsdown_us-east1-b_headsdown.yaml --set image=$IMG:$TAG
