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

commit_sha="${2}"
short_sha="${commit_sha::8}"
if [[ -z "${commit_sha}" ]]; then
  commit_sha="locally-triggered"
  short_sha="${commit_sha}"
fi

bash_escape (){
  printf "%q\n" "${1}"
}

bash_escape "BRANCH_NAME=${branch_name}" >> "${env_file}"

bash_escape "COMMIT_SHA=${commit_sha}" >> "${env_file}"

image_tag_for_run="${branch_name}-${short_sha}-$(date +%s)"
bash_escape "RUNTIME_IMAGE_NAME_FOR_RUN=${BUILD_CLOUD_RUNTIME_IMAGE_NAME}:${image_tag_for_run}" >> "${env_file}"
bash_escape "MANAGEMENT_IMAGE_NAME_FOR_RUN=${BUILD_CLOUD_RUNTIME_IMAGE_NAME}-dev-management:${image_tag_for_run}" >> "${env_file}"

# re-exports from gcloud_env_vars.sh
bash_escape "GITHUB_MAIN_BRANCH_NAME=${GITHUB_MAIN_BRANCH_NAME}" >> "${env_file}"
bash_escape "PROJECT_REGION=${PROJECT_REGION}" >> "${env_file}"
bash_escape "TEST_COVERAGE_BUCKET_NAME=${TEST_COVERAGE_BUCKET_NAME}" >> "${env_file}"
bash_escape "TEST_COVERAGE_THRESHOLD=${TEST_COVERAGE_THRESHOLD}" >> "${env_file}"
bash_escape "TEST_DELTA_THRESHOLD=${TEST_DELTA_THRESHOLD}" >> "${env_file}"
