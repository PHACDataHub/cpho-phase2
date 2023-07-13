#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

env_file=$(dirname "${BASH_SOURCE[0]}")/../server/.env.prod

rm -f "${env_file}"

touch "${env_file}"

# NON-secret configurations only in here, Cloud Run jobs will deploy with the actuan secrets (DB password, Django secret key, etc) as env vars
# Include placeholder values for secrets, or else you won't be able to run collect static as a Docker build time step

bash_escape "DB_NAME=${DB_NAME}" >> "${env_file}"
bash_escape "DB_USER=${DB_USER}" >> "${env_file}"
bash_escape "DB_PASSWORD=PLACEHOLDER_FOR_SECRET" >> "${env_file}"
bash_escape "DB_HOST=$(gcloud sql instances list --filter name:"${DB_INSTANCE_NAME}" --format "value(PRIVATE_ADDRESS)")" >> "${env_file}"
bash_escape "DB_PORT=5432" >> "${env_file}"

bash_escape "SECRET_KEY=PLACEHOLDER_FOR_SECRET" >> "${env_file}"

# Prior to the first deploy, the service doesn't exist yet and it's URL is unknown (TODO: well, this will change when the project has a domain name)
service_url=$(gcloud run services describe "${PROJECT_SERVICE_NAME}" --platform managed --region "${PROJECT_REGION}" --format "value(status.url)" || echo "")
if [[ ! -z $service_url ]]; then
  # Need to strip the https:// from the URL, just want the host portion
  ALLOWED_HOSTS=$(echo "${service_url}" | sed 's/^https:\/\///')
else
  # Fall back to 
  ALLOWED_HOSTS=.
fi
bash_escape "ALLOWED_HOSTS=${ALLOWED_HOSTS}" >> "${env_file}"

if [[ ! $PROJECT_IS_USING_WHITENOISE ]]; then
  bash_escape "MEDIA_BUCKET_NAME=${MEDIA_BUCKET_NAME}" >> "${env_file}"
fi
