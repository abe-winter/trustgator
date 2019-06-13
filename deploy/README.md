# deployment

## Checklist

1. check `kubectl config current-context` should make sense
1. check `gcloud config configurations list` (if relevant to you)
1. ideally git is clean (no modifications in `git status`)
1. run `deploy/build.sh` to upload a docker build and set `.lastbuild`
1. run `deploy/deploy.sh` to deploy .lastbuild to kube (using helm)

## DB migrations

Are incredible painful. You have to shell into the trustgator pod and run the specific missing migrations:

```bash
apt update && apt install -qqy postgresql-client
PGPASSWORD=$DBPASS psql -U $DBUSER -h $DBHOST -f sql/migrate/*.sql
```

## One-time prep on gcloud

1. you can do `gcloud config configurations create $YOURCONFIG` and `gcloud init` if missing a $YOURCONFIG config in gcloud
1. create a [service acct for cloud sql proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy#create-service-account) and upload it to kube
  - `kubectl create secret generic cloudsql --from-file=something.json`

## One-time prep on all platforms

1. prep letsencrypt namespace:
	- https://docs.cert-manager.io/en/latest/getting-started/install.html
	- I used the 'regular manifests' instructions and had to `--validate=false` in the `kubetctl apply` step
1. run the apply-schema job (todo: migrations aren't automatic yet)
1. create secrets with DB & flask-session passwords
1. install helm on your cluster with ./install-helm.sh
1. `helm repo add kiwigrid https://kiwigrid.github.io` (ugh -- why isn't this automatic from requirements.yaml? bitrot)
1. install the chart with `helm install -f trustgator/values_gke_headsdown_us-east1-b_headsdown.yaml --name trustgator ./trustgator`

## Dev help

* you can debug template evaluation with `helm install --debug --dry-run ./trustgator`
