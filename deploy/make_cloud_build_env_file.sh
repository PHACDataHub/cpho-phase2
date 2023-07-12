#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

env_file=$(dirname "${BASH_SOURCE[0]}")/../.env.cloud_build

rm -f "${env_file}"

touch "${env_file}"

bash_escape "PROJECT_SERVICE_NAME=${PROJECT_SERVICE_NAME}" >> "${env_file}"

bash_escape "PROJECT_REGION=${PROJECT_REGION}" >> "${env_file}"

bash_escape "BUILD_CLOUD_RUN_IMAGE_NAME=${BUILD_CLOUD_RUN_IMAGE_NAME}" >> "${env_file}"

bash_escape "DB_INSTANCE_NAME=${DB_INSTANCE_NAME}" >> "${env_file}"

bash_escape "VPC_CONNECTOR_NAME=${VPC_CONNECTOR_NAME}" >> "${env_file}"
 