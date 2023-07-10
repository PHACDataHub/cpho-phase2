#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

ENV_FILE=$(dirname "${BASH_SOURCE[0]}")/../.env.cloud_build

rm -f ${ENV_FILE}

touch ${ENV_FILE}

bash_escape PROJECT_SERVICE_NAME=${PROJECT_SERVICE_NAME} >> ${ENV_FILE}

bash_escape PROJECT_REGION=${PROJECT_REGION} >> ${ENV_FILE}

bash_escape BUILD_CLOUD_RUN_IMAGE_NAME=${BUILD_CLOUD_RUN_IMAGE_NAME} >> ${ENV_FILE}

bash_escape DB_INSTANCE_NAME=${DB_INSTANCE_NAME} >> ${ENV_FILE}

bash_escape VPC_CONNECTOR_NAME=${VPC_CONNECTOR_NAME} >> ${ENV_FILE}
 