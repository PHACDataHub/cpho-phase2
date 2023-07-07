#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source ./deploy/gcloud_env_vars.sh

PROD_ENV_FILE=".env.prod"

rm -f ${PROD_ENV_FILE}

touch ${PROD_ENV_FILE}

escape (){
  printf "%q\n" $1
}

escape DB_NAME=${DB_NAME} >> ${PROD_ENV_FILE}
escape DB_USER=${DB_USER} >> ${PROD_ENV_FILE}
escape DB_PASSWORD=$(get_secret ${SKEY_DB_USER_PASSWORD}) >> ${PROD_ENV_FILE}
escape DB_HOST=$(gcloud sql instances list --filter name:${DB_INSTANCE_NAME} --format "value(PRIVATE_ADDRESS)") >> ${PROD_ENV_FILE}
escape DB_PORT=5432 >> ${PROD_ENV_FILE}

escape SECRET_KEY=$(get_secret ${SKEY_DJANGO_SECRET_KEY}) >> ${PROD_ENV_FILE}

# Prior to the first deploy, the service doesn't exist yet and it's URL is unknown (TODO: well, this will change when the project has a domain name)
SERVICE_URL=$(gcloud run services describe ${PROJECT_SERVICE_NAME} --platform managed --region ${PROJECT_REGION} --format "value(status.url)" || echo "")
if [[ ! -z $SERVICE_URL ]]; then
  # Need to strip the https:// from the URL, just want the host portion
  ALLOWED_HOSTS=$(echo ${SERVICE_URL} | sed 's/^https:\/\///')
else
  # Fall back to allowing any sub domain of run.app, just for the initial deploy
  ALLOWED_HOSTS=.run.app
fi
escape ALLOWED_HOSTS=${ALLOWED_HOSTS} >> ${PROD_ENV_FILE}

if [[ ! $PROJECT_IS_USING_WHITENOISE ]]; then
  escape MEDIA_BUCKET_NAME=${MEDIA_BUCKET_NAME} >> ${PROD_ENV_FILE}
fi
