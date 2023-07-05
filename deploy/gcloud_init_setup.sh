#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source ./deploy/gcloud_env_vars.sh



# TODO replace with Infrastructure as Code/Data, after the options are discussed and we agree on one (with app devs included in discussion)



# ----- SECRET MANAGER -----
echo ""
echo "Create and store secrets (and less-secret configuration values for the prod env)"
read -n 1 -p "Type S to skip this step, anything else to continue: " SECRETS_SKIP
echo ""
if [[ $SECRETS_SKIP != "S" ]]; then
  gcloud services enable secretmanager.googleapis.com
  
    set_secret ${SKEY_DB_INSTANCE_NAME} ${DB_INSTANCE_NAME}
    set_secret ${SKEY_DB_NAME} ${DB_NAME}
    set_secret ${SKEY_DB_USER} ${DB_USER}
    set_secret ${SKEY_DB_USER_PASSWORD} $(openssl rand -base64 100 | tr -dc a-zA-Z0-9)
    set_secret ${SKEY_DB_ROOT_PASSWORD} $(openssl rand -base64 100 | tr -dc a-zA-Z0-9)
    set_secret ${SKEY_DB_URL} postgres://${DB_USER}:$(get_secret $SKEY_DB_USER_PASSWORD)@//cloudsql/${PROJECT_ID}:${PROJECT_REGION}:${DB_INSTANCE_NAME}/${DB_NAME}
  
    set_secret ${SKEY_DJANGO_SECRET_KEY} $(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
  
  if [ ! ${PROJECT_IS_USING_WHITENOISE} ]; then
      set_secret ${SKEY_MEDIA_BUCKET_NAME} ${MEDIA_BUCKET_NAME}
  fi
fi



# ----- ARTIFACT REGISTRY -----
echo ""
echo "Enable Artifact Registry to store container images for Cloud Run to use"
read -n 1 -p "Type S to skip this step, anything else to continue: " ARTIFACT_SKIP
echo ""
if [[ $ARTIFACT_SKIP != "S" ]]; then
  gcloud services enable artifactregistry.googleapis.com
  
  # Create Artifact Repo within the Artifact Registry
  gcloud artifacts repositories create $ARTIFACT_REGISTRY_REPO \
     --location ${PROJECT_REGION} \
     --description ${ARTIFACT_REGISTRY_REPO} \
     --repository-format docker 
  
  # Authorize local docker client to push/pull images to artifact registry
  gcloud auth configure-docker ${PROJECT_REGION}-docker.pkg.dev
fi



# ----- CLOUD BUILD ----
echo ""
echo "Enable Cloud Build, triggered by GitHub pushes"
read -n 1 -p "Type S to skip this step, anything else to continue: " BUILD_SKIP
echo ""
if [[ $BUILD_SKIP != "S" ]]; then
  gcloud services enable \
    cloudbuild.googleapis.com \
    sourcerepo.googleapis.com
  
  # _Can_ be done more programatically, but it's messy. Just do this manually for now
  read -n 1 -p "Manual step: via the GCP dashboard for this project, navigate to Cloud Build > Repositories and use \"CONNECT TO REPOSITORY\" to grant access to your GitHub repo. Press any key to continue: "
  
  # Add cloud build trigger (this is set to be triggered on push to main branch)
  gcloud builds triggers create github \
    --name ${BUILD_CLOUD_BUILD_TRIGGER_NAME} \
    --region ${PROJECT_REGION} \
    --repo-name ${BUILD_GITHUB_REPO_NAME} \
    --repo-owner ${BUILD_GITHUB_REPO_OWNER} \
    --branch-pattern ${BUILD_TRIGGER_BRANCH_PATTERN} \
    --build-config ${BUILD_CLOUD_BUILD_CONFIG_PATH} \
    --include-logs-with-status \
    --no-require-approval
  
  # Bind permissions to Cloud Build service account:
  gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role roles/cloudbuild.serviceAgent \
    --role roles/run.admin \
    --role roles/artifactregistry.writer \
    --role roles/cloudsql.client \
    --role roles/iam.serviceAccountUser \
    --condition None
  
  # Give the Cloud Build service account access to prod secrets
  for SKEY in ${PROD_ENV_SECRET_KEYS[@]}; do
    gcloud secrets add-iam-policy-binding ${SKEY} \
      --member serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
      --role roles/secretmanager.secretAccessor
  done
  
  
  # MANUAL: write a cloudbuild.yaml, commit it in the repo root
  # To test-run your cloudbuild.yaml, use: gcloud builds submit --config cloudbuild.yaml
fi



# ----- CLOUD RUN -----
echo ""
echo "Enable the Cloud Run API and grant it access to necessary resources"
read -n 1 -p "Type S to skip this step, anything else to continue: " RUN_SKIP
echo ""
if [[ $RUN_SKIP != "S" ]]; then
  gcloud services enable \
    run.googleapis.com \
    compute.googleapis.com
  
  gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role roles/run.admin
  
  # Grant the IAM Service Account User role to the Cloud Build service account for the Cloud Run runtime service account
  gcloud iam service-accounts add-iam-policy-binding ${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --member serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role roles/iam.serviceAccountUser
fi



# ----- CLOUD STORAGE (optional) -----
if [ ! $PROJECT_IS_USING_WHITENOISE ]; then
  echo ""
  echo "Create a media bucket"
  read -n 1 -p "Type S to skip this step, anything else to continue: " BUCKET_SKIP
  echo ""
  if [[ $BUCKET_SKIP != "S" ]]; then
    gsutil mb -l ${PROJECT_REGION} gs://${MEDIA_BUCKET_NAME}
  fi
fi



# ----- CLOUD SQL -----
echo ""
echo "Enable the Cloud SQL API, create a database and user"
read -n 1 -p "Type S to skip this step, anything else to continue: " SQL_SKIP
echo ""
if [[ $SQL_SKIP != "S" ]]; then
  # Enable APIs
  gcloud services enable \
    sql-component.googleapis.com \
    sqladmin.googleapis.com 
  
  # Create Postgres instance
  gcloud sql instances create ${DB_INSTANCE_NAME} \
    --project ${PROJECT_ID} \
    --database-version ${DB_VERSION} \
    --tier ${DB_TIER} \
    --region ${PROJECT_REGION} \
    --root-password $(get_secret ${SKEY_DB_ROOT_PASSWORD})
  
  # Create Database
  gcloud sql databases create ${DB_NAME} \
    --instance ${DB_INSTANCE_NAME}
  
  #Create User
  gcloud sql users create ${DB_USER} \
    --instance ${DB_INSTANCE_NAME} \
    --password $(get_secret ${SKEY_DB_ROOT_PASSWORD})
fi

# See step six in deploy/README.md, you'll need to connect to this database via cloud SQL proxy and perform initial migrations and data seeding

# OPTION 1: cloud SQL proxy (WIP) 
# in another terminal set environment variables
# export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
# export USE_CLOUD_SQL_AUTH_PROXY=true

# get DB root user password from gcloud secrets
# gcloud secrets versions access latest --secret ${DB_ROOT_PASSWORD_KEY} && echo ""

# can locally connect python manage.py runserver


# OPTION 2: cloud run job (WIP) (fragments below are using cloud build to do this, but it should be a one off cloud run job instead)
# deploy cloud build, run database migrations and populate static assests

# Give the Cloud Build service user access to the DB ${DB_ROOT_PASSWORD_KEY} secret
# gcloud secrets add-iam-policy-binding ${DB_ROOT_PASSWORD_KEY} \
#   --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
#   --role=roles/secretmanager.secretAccessor

# gcloud builds submit --config cloudbuild.yaml \
#   --substitutions _DB_INSTANCE_NAME=test-instance, _REGION=northamerica-northeast1

# SERVICE_URL=$(gcloud run services describe $PROJECT_SERVICE_NAME --platform managed \
#   --region northamerica-northeast1 --format "value(status.url)")

# gcloud run services update $PROJECT_SERVICE_NAME \
#   --platform managed \
#   --region northamerica-northeast1 \
#   --set-env-vars CLOUDRUN_SERVICE_URL=$SERVICE_URL


# # to run - add deploy step to yaml and 
# gcloud builds submit --config cloudbuild.yaml or add trigger

# Remove Cloud Build service ${DB_ROOT_PASSWORD_KEY} secret access
# gcloud secrets remove-iam-policy-binding ${DB_ROOT_PASSWORD_KEY} \
#   --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
#   --role=roles/secretmanager.secretAccessor



# ----- TODOs -----
# Borrow the pulumi for Cloud Run networking from https://github.com/PHACDataHub/phac-epi-garden/tree/main/deploy
