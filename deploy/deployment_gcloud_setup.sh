
#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
 
# Mostly steps from google run tutorial from: https://cloud.google.com/sql/docs/postgres/connect-run
# ** WIP, NOT a runnable shell script - yet -. This will all incorperated into infrasturcture as code in the future. 
EXIT

# ----- SET UP ENVIRONMENT VARIABLES -----
export PROJECT_ID=pdcp-cloud-006-cpho
export PROJECT_NUMBER=$(gcloud projects describe ${PROJECT_ID} --format="value(projectNumber)")
export REGION=northamerica-northeast1
export SERVICE_NAME=cpho-phase2
export SECRET_SETTINGS_NAME=django_settings
export ARTIFACT_REGISTRY_REPO=cpho-artifact-registry-for-cloud-run
export INSTANCE_NAME=cpho-db-instance
export DB_NAME=cpho_dev_db
export DB_USER=cpho_db_user
export CLOUD_BUILD_TRIGGER_NAME=cpho-github-main-branch-trigger
export GITHUB_REPO_NAME=cpho-phase2
export CLOUD_BUILD_CONFIG_PATH=cloudbuild.yaml
export GITHUB_REPO_OWNER=PHACDataHub

export DB_PASSWORD=password123 #OR generate and then save to GCP secrets: $(openssl rand -base64 16 | tr -dc A-Za-z0-9 | head -c16 ; echo '')

export DB_ROOT_PASSWORD=password123 #OR generate and then save to GCP secrets: $(openssl rand -base64 16 | tr -dc A-Za-z0-9 | head -c16 ; echo '')
export DB_ROOT_PASSWORD_KEY=db_root_user_password


# ----- SECRET MANAGER -----
# Enable API
gcloud services enable secretmanager.googleapis.com

# create prod .env secrets, store by $SECRET_SETTINGS_NAME key
rm .env.prod
echo DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@//cloudsql/${PROJECT_ID}:${REGION}:${INSTANCE_NAME}/${DB_NAME} > .env.prod
echo SECRET_KEY=$(cat /dev/urandom | LC_ALL=C tr -dc '[:alpha:]'| fold -w 50 | head -n1) >> .env.prod
# echo GS_BUCKET_NAME=${PROJECT_ID}_MEDIA_BUCKET >> .env.prod

# TODO, maybe a MANUAL step, but need other values in the .env.prod file before saving it in secrets

# store django_settings secrets
gcloud secrets create --locations ${REGION} --replication-policy user-managed ${SECRET_SETTINGS_NAME} --data-file .env.prod
rm .env.prod

# store DB root user password as separate secret, for later user
echo $DB_ROOT_PASSWORD | gcloud secrets create --locations ${REGION} --replication-policy user-managed ${DB_ROOT_PASSWORD_KEY} --data-file -

# OR if secret already exists, and just need to UPDATE
# gcloud secrets versions add ${SECRET_SETTINGS_NAME} \
#     --data-file=.env \
#     --project=${PROJECT_ID}

# To verify that this worked
# gcloud secrets describe ${SECRET_SETTINGS_NAME}
# (or gcloud secrets list)

# gcloud secrets versions access latest --secret ${SECRET_SETTINGS_NAME}  #django_settings



# ----- ARTIFACT REGISTRY -----
# Enable Artifact Registry to store container images for Cloud Run to use 
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Repo within the Artifact Registry
gcloud artifacts repositories create $ARTIFACT_REGISTRY_REPO \
   --location=$REGION \
   --description=$ARTIFACT_REGISTRY_REPO \
   --repository-format=docker 

# Authorize docker to push images to artifact registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev



# ----- CLOUD BUILD ----
# Set up Cloud Build  (https://cloud.google.com/sdk/gcloud/reference/beta/builds/triggers/create/github)
# On push to main branch in specified GitHub repo, Cloud Build is triggered to run the steps outlined in cloudbuild.yaml: 
# building and pushing Docker image to Artifact Registry, running migration, and populating static files, then deploy to Cloud Run with connection to Cloud SQL

gcloud services enable \
  cloudbuild.googleapis.com \
  sourcerepo.googleapis.com

# MANUAL: via the GCP dashboard, navigate to Cloud Build > Repositories and use "CONNECT TO REPOSITORY" to grant access to your GitHub repo
# _can_ be done more programatically, but it's messy. Just do this manually for now

# MANUAL: write a cloudbuild.yaml, commit it in the repo root
# To test-run your cloudbuild.yaml, use `gcloud builds submit --config cloudbuild.yaml` 

# Add cloud build trigger (this is set to be triggered on push to main branch)
gcloud builds triggers create github \
  --name=${CLOUD_BUILD_TRIGGER_NAME} \
  --region ${REGION} \
  --repo-name=${GITHUB_REPO_NAME} \
  --repo-owner=${GITHUB_REPO_OWNER} \
  --branch-pattern="^main$" \
  --build-config=${CLOUD_BUILD_CONFIG_PATH} \
  --include-logs-with-status \
  --no-require-approval

# Bind permissions to Cloud Build service account:
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
    --role=roles/cloudbuild.serviceAgent \
    --role=roles/run.admin \
    --role=roles/artifactregistry.writer \
    --role=roles/secretmanager.secretAccessor \
    --role=roles/cloudsql.client \
    --role=roles/iam.serviceAccountUser
    --condition='' # Okay this didn't work - needs condition manualy set to None with asked in terminal

# Give the Cloud Build service user access to the $SECRET_SETTINGS_NAME secrets
gcloud secrets add-iam-policy-binding $SECRET_SETTINGS_NAME \
  --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor



# ----- CLOUD RUN -----
# Enable Cloud Run API    
gcloud services enable run.googleapis.com
    \ compute.googleapis.com

gcloud projects add-iam-policy-binding $PROJECT_ID\
    --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/run.admin

# Grant the IAM Service Account User role to the Cloud Build service account for the Cloud Run runtime service account
gcloud iam service-accounts add-iam-policy-binding $PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
    --role=roles/iam.serviceAccountUser

# Give the Cloud Run service user access to the $SECRET_SETTINGS_NAME secrets
gcloud secrets add-iam-policy-binding $SECRET_SETTINGS_NAME \
    --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor 



# ----- CLOUD STORAGE (optional) -----
# skipping for now, as we're planning to use whitenoise and serve static files via the app instances

# GS_BUCKET_NAME=${PROJECT_ID}_MEDIA_BUCKET
# gsutil mb -l ${REGION} gs://${GS_BUCKET_NAME}



# ----- CLOUD SQL -----
# 1. Enable Cloud SQL API
# 2. Bind Service Account to have Secret Acessor role
# 2. Create the container instance 
# 2. Create the database
# 3. Create a user to access database
# https://cloud.google.com/sql/docs/sqlserver/create-manage-databases#gcloud

# Enable APIs
gcloud services enable \
  sql-component.googleapis.com \
  sqladmin.googleapis.com 

# Create Postgres instance
gcloud sql instances create ${INSTANCE_NAME} \
    --project ${PROJECT_ID} \
    --database-version POSTGRES_14 \
    --tier db-g1-small \
    --region ${REGION} \
    --root-password="${DB_ROOT_PASSWORD}"

# Create Database
gcloud sql databases create ${DB_NAME} \
    --instance ${INSTANCE_NAME}

#Create User
gcloud sql users create ${DB_USER} \
    --instance ${INSTANCE_NAME} \
    --password ${DB_PASSWORD}


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
#     --substitutions _INSTANCE_NAME=test-instance, _REGION=northamerica-northeast1

# SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed \
#     --region northamerica-northeast1 --format "value(status.url)")

# gcloud run services update $SERVICE_NAME \
#     --platform managed \
#     --region northamerica-northeast1 \
#     --set-env-vars CLOUDRUN_SERVICE_URL=$SERVICE_URL


# # to run - add deploy step to yaml and 
# gcloud builds submit --config cloudbuild.yaml or add trigger
# ```

# Remove Cloud Build service ${DB_ROOT_PASSWORD_KEY} secret access
# gcloud secrets remove-iam-policy-binding ${DB_ROOT_PASSWORD_KEY} \
#   --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
#   --role=roles/secretmanager.secretAccessor
