#!/usr/bin/env bash

# This script is meant to be called via `source`, so forgo the standard `set -o ...` boilerplate 

# NON-SECRET configuration values ONLY! 
# Secret values live exclusively in GCP secrets, although their keys (might) be stored here
# Fetch secret values as needed with the get_secret helper function exported below

#####################
# Project dependent #
#####################

export PROJECT_ID=phx-01h4rr1468rj3v5k60b1vserd3
export PROJECT_REGION=northamerica-northeast1

export PROJECT_SERVICE_NAME=cpho-phase2
export PROJECT_ALPHA_SUB_DOMAIN=hopic-sdpac

export BUILD_GITHUB_REPO_NAME=cpho-phase2
export BUILD_GITHUB_REPO_OWNER=PHACDataHub

export GITHUB_MAIN_BRANCH_NAME=main

export TEST_COVERAGE_BUCKET_NAME=hopic-test-coverage-reports
export TEST_COVERAGE_THRESHOLD=77.5 # set just below current coverage, consider increasing in time
export TEST_DELTA_THRESHOLD=-2  # % value, threshold for current commit test coverage minus last commit on main's coverage

export APP_HEALTHCHECK_ROUTE=/healthcheck
export SLACK_ALERTING_CHANNEL_NAME="#cpho-hopic-prod-alerts"

# NOTE: if PROJECT_IS_USING_WHITENOISE is true then no media cloud storage will be created for the project
export PROJECT_IS_USING_WHITENOISE=true

#########################################
# Derived & less likely to need changes #
#########################################

gcloud config set project "${PROJECT_ID}"
gcloud config set compute/region "${PROJECT_REGION}"

# ----- PROJECT -----
export PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format="value(projectNumber)")

# ----- CLOUD DNS  -----
# phac-alpha DNS vars
export DNS_PHAC_ALPHA_DOMAIN="phac-aspc.alpha.canada.ca"
export DNS_PHAC_ALPHA_NAME="phac-aspc-alpha-canada-ca"
export DNS_PHAC_ALPHA_NS_NAME="alpha-dns"
# project DNS vars
export DNS_MANAGED_ZONE_NAME="${PROJECT_SERVICE_NAME}-managed-dns-zone"
export DNS_DOMAIN="${PROJECT_ALPHA_SUB_DOMAIN}.${DNS_PHAC_ALPHA_DOMAIN}"
export DNS_DNS_NAME="${DNS_DOMAIN}."
export DNS_ZONE_NAME="${PROJECT_ALPHA_SUB_DOMAIN}-${DNS_PHAC_ALPHA_NAME}-zone"
export DNS_NS_NAME="${PROJECT_ALPHA_SUB_DOMAIN}-${DNS_PHAC_ALPHA_NAME}-ns"

# ----- INGRESS NETWORKING -----
export INGRESS_NEG_NAME="${PROJECT_SERVICE_NAME}-network-endpoint-group"
export INGRESS_BACKEND_SERVICE_NAME="${PROJECT_SERVICE_NAME}-network-backend-service"
export INGRESS_BASELINE_SECURITY_POLICY_NAME="${PROJECT_SERVICE_NAME}-baseline-security-policies-for-load-balancer"
export INGRESS_URL_MAP_NAME="${PROJECT_SERVICE_NAME}-url-map"
export INGRESS_SSL_CERT_NAME="${PROJECT_SERVICE_NAME}-cert"
export INGRESS_TARGET_HTTPS_PROXY_NAME="${PROJECT_SERVICE_NAME}-https-proxy"
export INGRESS_FORWARDING_IP_NAME="${PROJECT_SERVICE_NAME}-forwarding-rule-ip"
export INGRESS_HTTPS_FORWARDING_RULE_NAME="${PROJECT_SERVICE_NAME}-https-forwarding-rule"

# ----- ARTIFACT REGISTRY -----
export ARTIFACT_REGISTRY_REPO="${PROJECT_SERVICE_NAME}-artifact-registry-for-cloud-run"

# ----- CLOUD BUILD ----
export BUILD_SQL_INSTANCE_LIST_ROLE_NAME=sqlInstanceLister
export BUILD_CLOUD_BUILD_TRIGGER_NAME="${PROJECT_SERVICE_NAME}-github-main-branch-trigger"
export BUILD_CLOUD_BUILD_CONFIG_PATH=cloudbuild.yaml
export BUILD_CLOUD_RUN_IMAGE_NAME="${PROJECT_REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${BUILD_GITHUB_REPO_NAME}"

# ----- CLOUD STORAGE -----
export MEDIA_BUCKET_NAME="${PROJECT_SERVICE_NAME}_MEDIA_BUCKET"

# ----- CLOUD SQL -----
export DB_VERSION=POSTGRES_14
export DB_TIER=db-g1-small
export DB_INSTANCE_NAME="${PROJECT_SERVICE_NAME}-db-instance"
export DB_NAME="${PROJECT_SERVICE_NAME}_db"
export DB_APP_USER="${PROJECT_SERVICE_NAME}_db_user"
export DB_LOCAL_ACCESS_USER="${PROJECT_SERVICE_NAME}_db_local_access_user"

# ----- LOCAL ACCESS TO PROD DB -----
export LOCAL_ACCESS_DB_PORT=6543

# ----- VPC NETWORK -----
export VPC_NAME=default
export VPC_SERVICE_CONNECTION_NAME="${PROJECT_SERVICE_NAME}-google-managed-services-${VPC_NAME}"
export VPC_CONNECTOR_NAME="${PROJECT_SERVICE_NAME}-sql-to-run"
export VPC_CONNECTOR_RANGE="10.8.0.0/28" # must be /28 and unused. 10.8.0.0 should be unused in a fresh project; pick something else otherwise

# ----- SECRET MANAGER (keys only) -----
export SKEY_DB_ROOT_PASSWORD=db_root_password
export SKEY_DB_APP_USER_PASSWORD_TEMP=db_app_user_password_temp
export SKEY_DB_LOCAL_ACCESS_USER_PASSWORD_TEMP=db_local_access_user_password_temp
export SKEY_PROD_ENV_FILE=django_production_env
export SKEY_LOCAL_ACCESS_PROD_ENV_FILE=django_local_prod_db_access_env
export SKEY_PROD_SLACK_ALERTING_APP_TOKEN=slack_alerting_app_token


set_secret () {
  local key="${1}"
  local value="${2}"

  if [[ -n $(gcloud secrets describe --verbosity none "${key}")  ]]; then
    echo $value | gcloud secrets versions add "${key}" --data-file -
  else
    echo $value | gcloud secrets create --locations "${PROJECT_REGION}" --replication-policy user-managed "${key}" --data-file -
  fi
}
export -f set_secret

get_secret () {
  local key="${1}"

  echo $(gcloud secrets versions access latest --secret "${key}")
}
export -f get_secret

# not a secret helper, but will occasionally be needed alongside get_secret
bash_escape (){
  printf "%q\n" "${1}"
}

delete_secret () {
  local key="${1}"

  if [[ -n $(gcloud secrets describe --verbosity none "${key}") ]]; then
    gcloud secrets delete "${key}"
  fi
}
export -f delete_secret
