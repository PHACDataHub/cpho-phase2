#!/usr/bin/env bash

# This script is meant to be called via `source`, so forgo the standard `set -o ...` boilerplate 

# NON-SECRET configuration values ONLY! 
# Secret values live exclusively in GCP secrets, although their keys (might) be stored here
# Fetch secret values as needed with the get_secret helper function exported below

#####################
# Project dependent #
#####################

export PROJECT_ID=pht-01hp04dtnkf
export PROJECT_REGION=northamerica-northeast1

export PROJECT_SERVICE_NAME=hopic
export PROJECT_ALPHA_SUB_DOMAIN=hopic-sdpac

export BUILD_GITHUB_REPO_NAME=cpho-phase2
export BUILD_GITHUB_REPO_OWNER=PHACDataHub

export GITHUB_MAIN_BRANCH_NAME=distroless-runtime-and-management-image

export TEST_COVERAGE_BUCKET_NAME=hopic-test-coverage-reports-01hp04dtnkf
export TEST_COVERAGE_THRESHOLD=77.5 # set just below current coverage, consider increasing in time
export TEST_DELTA_THRESHOLD=-2  # % value, threshold for current commit test coverage minus last commit on main's coverage

export APP_HEALTHCHECK_ROUTE=/healthcheck
export SLACK_ALERTING_CHANNEL_NAME="#cpho-hopic-prod-alerts"

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
export DNS_MANAGED_ZONE_NAME="${PROJECT_SERVICE_NAME}-managed-zone"
export DNS_DOMAIN="${PROJECT_ALPHA_SUB_DOMAIN}.${DNS_PHAC_ALPHA_DOMAIN}"
export DNS_DNS_NAME="${DNS_DOMAIN}."
export DNS_NS_NAME="${PROJECT_ALPHA_SUB_DOMAIN}-${DNS_PHAC_ALPHA_NAME}-ns"

# ----- ARTIFACT REGISTRY -----
export ARTIFACT_REGISTRY_REPO="${PROJECT_SERVICE_NAME}-k8s-images"

# ----- CLOUD BUILD ----
export BUILD_CLOUD_BUILD_TRIGGER_NAME="${PROJECT_SERVICE_NAME}-cloudbuild-trigger"
export BUILD_CLOUD_BUILD_CONFIG_PATH=cloudbuild.yaml
export BUILD_CLOUD_RUNTIME_IMAGE_NAME="${PROJECT_REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${BUILD_GITHUB_REPO_NAME}"
export BUILD_CLOUD_MANAGEMENT_IMAGE_NAME="${BUILD_CLOUD_RUNTIME_IMAGE_NAME}-dev-management"

# ----- SECRET MANAGER (keys only) -----
export SKEY_PROD_SLACK_ALERTING_APP_TOKEN=slack_alerting_app_token
