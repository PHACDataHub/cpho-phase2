#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

env_file=$(dirname "${BASH_SOURCE[0]}")/../.env.cloud_build

rm -f "${env_file}"

touch "${env_file}"

# if cloud build is triggered locally, the built in substitutions (like BRANCH_NAME and COMMIT_SHA) will be empty,
# so in addition to supplying env vars out of gcloud_env_vars.sh, this script must set fallback values for
# any built in Cloud Build substitutions used
branch_name="${1}"
if [[ -z "${branch_name}" ]]; then
  branch_name=$(git rev-parse --abbrev-ref HEAD)
fi

commit_sha="${2}::8"
if [[ -z "${commit_sha}" ]]; then
  commit_sha="locally-triggerd"
fi

bash_escape "BRANCH_NAME=${branch_name}" >> "${env_file}"

bash_escape "COMMIT_SHA=${commit_sha}" >> "${env_file}"

bash_escape "IMAGE_NAME_FOR_RUN=${BUILD_CLOUD_RUN_IMAGE_NAME}:${branch_name}-${commit_sha}-$(date +%s)" >> "${env_file}"

# re-exports from gcloud_env_vars.sh
bash_escape "GITHUB_MAIN_BRANCH_NAME=${GITHUB_MAIN_BRANCH_NAME}" >> "${env_file}"
bash_escape "PROJECT_SERVICE_NAME=${PROJECT_SERVICE_NAME}" >> "${env_file}"
bash_escape "PROJECT_REGION=${PROJECT_REGION}" >> "${env_file}"
bash_escape "DB_INSTANCE_NAME=${DB_INSTANCE_NAME}" >> "${env_file}"
bash_escape "VPC_CONNECTOR_NAME=${VPC_CONNECTOR_NAME}" >> "${env_file}"
bash_escape "SKEY_PROD_ENV_FILE=${SKEY_PROD_ENV_FILE}" >> "${env_file}"
bash_escape "TEST_COVERAGE_BUCKET_NAME=${TEST_COVERAGE_BUCKET_NAME}" >> "${env_file}"
bash_escape "TEST_COVERAGE_THRESHOLD=${TEST_COVERAGE_THRESHOLD}" >> "${env_file}"
bash_escape "TEST_DELTA_THRESHOLD=${TEST_DELTA_THRESHOLD}" >> "${env_file}"
