#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source ./deploy/gcloud_env_vars.sh

PROD_ENV_FILE="./server/.env.prod"

rm -f ${PROD_ENV_FILE}

touch ${PROD_ENV_FILE}

cat <<EOT >> ${PROD_ENV_FILE}
DB_NAME=$(get_secret ${SKEY_DB_NAME})
DB_USER=$(get_secret ${SKEY_DB_USER})
DB_PASSWORD=$(get_secret ${SKEY_DB_USER_PASSWORD})
DB_HOST=$(gcloud sql instances describe ${SKEY_DB_INSTANCE_NAME} --format=json | jq -r '.ipAddresses[] | select(.type=="PRIMARY") | .ipAddress')
DB_PORT=5432

SECRET_KEY=$(get_secret ${SKEY_DJANGO_SECRET_KEY})

# This won't work on the first Cloud Run deploy, as the service won't have a URL yet
ALLOWED_HOSTS=[$(gcloud run services describe ${PROJECT_SERVICE_NAME} --platform managed --region REGION --format "value(status.url)")]

$(if [[ ! $PROJECT_IS_USING_WHITENOISE ]]; then; echo MEDIA_BUCKET_NAME=$(get_secret ${SKEY_MEDIA_BUCKET_NAME}); fi)
EOT
