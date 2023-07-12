#!/usr/bin/env bash

# This script is meant to be called via `source`, so forgo the standard `set -o ...` boilerplate 

# NON-SECRET configuration values ONLY! 
# Secret values live exclusively in GCP secrets, although their keys (might) be stored here
# Fetch secret values as needed with the get_secret helper function exported below

#####################
# Project dependent #
#####################

export PROJECT_ID=phx-01h4rr1468rj3v5k60b1vserd3
export PROJECT_SERVICE_NAME=cpho-phase2
export PROJECT_REGION=northamerica-northeast1

# NOTE: if PROJECT_IS_USING_WHITENOISE is False then no cloud storage will be created for the project
export PROJECT_IS_USING_WHITENOISE=True

export BUILD_GITHUB_REPO_NAME=cpho-phase2
export BUILD_GITHUB_REPO_OWNER=PHACDataHub
export BUILD_TRIGGER_BRANCH_PATTERN=^cloud-run-deployment$ #^main$

#########################################
# Derived & less likely to need changes #
#########################################

gcloud config set project ${PROJECT_ID}
gcloud config set compute/region ${PROJECT_REGION}

# ----- PROJECT -----
export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")

# ----- ARTIFACT REGISTRY -----
export ARTIFACT_REGISTRY_REPO=${PROJECT_SERVICE_NAME}-artifact-registry-for-cloud-run

# ----- CLOUD BUILD ----
export BUILD_SQL_INSTANCE_LIST_ROLE_NAME=sqlInstanceLister
export BUILD_CLOUD_BUILD_TRIGGER_NAME=${PROJECT_SERVICE_NAME}-github-main-branch-trigger
export BUILD_CLOUD_BUILD_CONFIG_PATH=cloudbuild.yaml
export BUILD_CLOUD_RUN_IMAGE_NAME=${PROJECT_REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${BUILD_GITHUB_REPO_NAME}

# ----- CLOUD STORAGE -----
export MEDIA_BUCKET_NAME=${PROJECT_SERVICE_NAME}_MEDIA_BUCKET

# ----- CLOUD SQL -----
export DB_VERSION=POSTGRES_14
export DB_TIER=db-g1-small
export DB_INSTANCE_NAME=${PROJECT_SERVICE_NAME}-db-instance
export DB_NAME=${PROJECT_SERVICE_NAME}_db
export DB_USER=${PROJECT_SERVICE_NAME}_db_user

# ----- VPC NETWORK -----
export VPC_NAME=default
export VPC_SERVICE_CONNECTION_NAME=${PROJECT_SERVICE_NAME}-google-managed-services-${VPC_NAME}
export VPC_CONNECTOR_NAME=${PROJECT_SERVICE_NAME}-sql-to-run
export VPC_CONNECTOR_RANGE=10.8.0.0/28 # must be /28 and unused. 10.8.0.0 should be unused in a fresh project; pick something else otherwise

# ----- SECRET MANAGER (keys only) -----
export SKEY_DB_USER_PASSWORD=db_user_password
export SKEY_DB_ROOT_PASSWORD=db_root_password
export SKEY_DB_URL=db_url

export SKEY_DJANGO_SECRET_KEY=django_secret_key

# Array of secret keys that Cloud Build needs access to (same set as those used in make_prod_env_file.sh, probably)
# Keep this up to date, the init setup script uses it to know what keys to give the relevant service accounts access to
PROD_ENV_SECRET_KEYS=($SKEY_DB_USER_PASSWORD $SKEY_DJANGO_SECRET_KEY)
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

# not a secret helper, but will occasionally be needed alongside get_secret
bash_escape (){
  printf "%q\n" $1
}

delete_secret () {
  local KEY=$1

  if [[ -n $(gcloud secrets describe --verbosity none ${KEY}) ]]; then
    gcloud secrets delete ${KEY}
  fi
}
export -f delete_secret