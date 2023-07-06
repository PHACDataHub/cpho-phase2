#!/usr/bin/env bash

# This script is meant to be called via `source`, so forgoe the standard `set -o ...` boilerplate 

# NON-SECRET configuration values ONLY! 
# Secret values live exclusively in GCP secrets, although their keys (might) be stored here. Fetch secrets as needed with the get_secret helper

# ----- PROJECT -----
export PROJECT_ID=phx-01h3m8rpdeyaf54w9ssf51syd5
export PROJECT_REGION=northamerica-northeast1
export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
export PROJECT_SERVICE_NAME=cpho-phase2

gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${PROJECT_REGION}

# ----- ARTIFACT REGISTRY -----
export ARTIFACT_REGISTRY_REPO=cpho-artifact-registry-for-cloud-run

# ----- CLOUD BUILD ----
export BUILD_CLOUD_BUILD_TRIGGER_NAME=cpho-github-main-branch-trigger
export BUILD_GITHUB_REPO_NAME=cpho-phase2
export BUILD_CLOUD_BUILD_CONFIG_PATH=cloudbuild.yaml
export BUILD_GITHUB_REPO_OWNER=PHACDataHub
export BUILD_TRIGGER_BRANCH_PATTERN=^main$

# ----- CLOUD STORAGE -----
# NOTE: if PROJECT_IS_USING_WHITENOISE is False then no media bucket will be created for the project
export PROJECT_IS_USING_WHITENOISE=True
export MEDIA_BUCKET_NAME=${PROJECT_ID}_MEDIA_BUCKET

# ----- CLOUD SQL -----
export DB_VERSION=POSTGRES_14 # aren't they using 13?
export DB_TIER=db-g1-small
export DB_INSTANCE_NAME=cpho-db-instance
export DB_NAME=cpho_dev_db
export DB_USER=cpho_db_user



# ----- SECRET MANAGER (keys, no values set here) -----
# Likely no need to edit these for a new project; doing so may break other scripts too, if they hard code against these secret names
export SKEY_DB_INSTANCE_NAME=db_instance_name
export SKEY_DB_NAME=db_name
export SKEY_DB_USER=db_user
export SKEY_DB_USER_PASSWORD=db_user_password
export SKEY_DB_ROOT_PASSWORD=db_root_password
export SKEY_DB_URL=db_url

export SKEY_DJANGO_SECRET_KEY=django_secret_key

export SKEY_MEDIA_BUCKET_NAME=media_bucket_name

# Array of secret keys that Cloud Build needs access to (same set as those used in make_prod_env_file.sh, probably)
# Keep this up to date, the init setup script uses it to know what keys to give the relevant service accounts access to
PROD_ENV_SECRET_KEYS=($SKEY_DB_NAME $SKEY_DB_USER $SKEY_DB_USER_PASSWORD $SKEY_DB_INSTANCE_NAME $SKEY_DJANGO_SECRET_KEY)
if [[ ! $PROJECT_IS_USING_WHITENOISE ]]; then
  PROD_ENV_SECRET_KEYS+=$SKEY_MEDIA_BUCKET_NAME
fi
export PROD_ENV_SECRET_KEYS


set_secret () {
  local KEY=$1
  local VALUE=$2

  if [[ -n $(gcloud secrets describe --verbosity none ${KEY})  ]]; then
    echo $VALUE | gcloud secrets versions add ${KEY} --data-file -
  else
    echo $VALUE | gcloud secrets create --locations ${PROJECT_REGION} --replication-policy user-managed ${KEY} --data-file -
  fi
}
export -f set_secret

get_secret () {
  local KEY=$1

  echo $(gcloud secrets versions access latest --secret ${KEY})
}
export -f get_secret

delete_secret () {
  local KEY=$1

  if [[ -n $(gcloud secrets describe --verbosity none ${KEY}) ]]; then
    gcloud secrets delete ${KEY}
  fi
}
export -f delete_secret