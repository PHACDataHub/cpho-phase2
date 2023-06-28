# Mostly steps from google run tutorial from: https://cloud.google.com/sql/docs/postgres/connect-run
** NOT a runnable shell script -yet - this will be incorperated into infrasturcture as code in the future. 

# ----- SET UP ENVIRONMENT VARIABLES -----
# # # If using terminal and running commands individually - use this:
# export PROJECT_ID=$(gcloud config get-value project) 
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
export USE_CLOUD_SQL_AUTH_PROXY=true
export DB_PASSWORD=password123 #OR
# export DB_PASSWORD=$(openssl rand -base64 16 | tr -dc A-Za-z0-9 | head -c16 ; echo '')



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

# Enable Cloud Build service and source repo
gcloud services enable cloudbuild.googleapis.com sourcerepo.googleapis.com

# ** Need to add cloudbuild.yaml to repo and the in Google Cloud console, connect Cloud Build to GitHub Repository 

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

# When this fails the first time, go connect repo to project in console

# To run without GitHub trigger: gcloud builds submit --config cloudbuild.yaml

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



# ----- CLOUD RUN -----
# Enable Cloud Run API    
gcloud services enable run.googleapis.com
gcloud services enable compute.googleapis.com

# Grant the IAM Service Account User role to the Cloud Build service account for the Cloud Run runtime service account
gcloud iam service-accounts add-iam-policy-binding \
    $PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --member=serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com \
    --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $PROJECT_ID\
    --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --role=roles/run.admin

# #Create CLOUD RUN service
# gcloud run deploy $SERVICE_NAME \
# --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/${SERVICE_NAME}" \
# --platform managed \
# --region $REGION \
# --add-cloudsql-instances "$PROJECT_ID:$REGION:$INSTANCE_NAME" \
# --allow-unauthenticated 


# ----- CLOUD SQL -----
1. Enable Cloud SQL API
2. Bind Service Account to have Secret Acessor role
2. Create the container instance 
2. Create the database
3. Create a user to access database

# https://cloud.google.com/sql/docs/sqlserver/create-manage-databases#gcloud

# # create db password & store in Secret Manager?
# export DB_PASSWORD=$(openssl rand -base64 16 | tr -dc A-Za-z0-9 | head -c16 ; echo '')
# echo -n "${DB_PASSWORD}" | gcloud secrets create DB_PASSWORD --replication-policy="user-managed" --locations="${REGION}" --data-file=-

# Enable APIs
gcloud services enable \
  sql-component.googleapis.com \
  sqladmin.googleapis.com 


# Create Postgres instance
gcloud sql instances create ${INSTANCE_NAME} \
    --project ${PROJECT_ID} \
    --database-version POSTGRES_14 \
    --tier db-g1-small \
    --region ${REGION}
    # --root-password="${DB_PASSWORD}"


# Create Database
gcloud sql databases create ${DB_NAME} \
    --instance ${INSTANCE_NAME}

#Create User
gcloud sql users create ${DB_USER} \
    --instance ${INSTANCE_NAME} \
    --password ${DB_PASSWORD}

# Create storage bucket (for static files, but may end up using whitenoise instead)
gsutil mb -l ${REGION}  gs://${PROJECT_ID}_MEDIA_BUCKET



# ---- SECRET MANAGER -----
# Enable API
gcloud services enable secretmanager.googleapis.com

# create secrets (Django settings)
echo DATABASE_URL=postgres://${DB_USER}:${DB_PASSWORD}@//cloudsql/${PROJECT_ID}:${REGION}:${INSTANCE_NAME}/${DB_NAME} > .env
# echo GS_BUCKET_NAME=${PROJECT_ID}_MEDIA_BUCKET >> .env
echo SECRET_KEY=$(cat /dev/urandom | LC_ALL=C tr -dc '[:alpha:]'| fold -w 50 | head -n1) >> .env

# store secrets
gcloud secrets create --locations ${REGION} --replication-policy user-managed ${SECRET_SETTINGS_NAME} --data-file .env

# Enable Cloud Run & cloud build to be able to access this 'Django settings' secret
gcloud secrets add-iam-policy-binding ${SECRET_SETTINGS_NAME} \
    --member=serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com \
    --role=roles/secretmanager.secretAccessor 

gcloud secrets add-iam-policy-binding ${SECRET_SETTINGS_NAME} \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor



gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/iam.serviceAccountUser

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
  --role=roles/run.admin



# # # OR if secret already exists, and just need to UPDATE
# gcloud secrets versions add ${SECRET_SETTINGS_NAME} \
#     --data-file=.env \
#     --project=${PROJECT_ID}

# # To verify that this worked
# gcloud secrets describe ${SECRET_SETTINGS_NAME}
# (or gcloud secrets list)

# gcloud secrets versions access latest --secret ${SECRET_SETTINGS_NAME}  #django_settings


#create database superuser and password
echo -n "$(cat /dev/urandom | LC_ALL=C tr -dc '[:alpha:]'| fold -w 30 | head -n1)" | gcloud secrets create --locations ${REGION} --replication-policy user-managed superuser_password --data-file -

# give cloud build access to this superuser password
gcloud secrets add-iam-policy-binding superuser_password \
    --member serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com \
    --role roles/secretmanager.secretAccessor


# in another terminal set environment variables
export GOOGLE_CLOUD_PROJECT=pdcp-cloud-006-cpho
export USE_CLOUD_SQL_AUTH_PROXY=true

export GOOGLE_CLOUD_PROJECT=$PROJECT_ID

# can locally connect python manage.py runserver

# # deploy cloud build, run database migrations and populate static assests
# gcloud builds submit --config cloudbuild.yaml \
#     --substitutions _INSTANCE_NAME=test-instance, _REGION=northamerica-northeast1



# save service url as environment variable

# SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed \
#     --region northamerica-northeast1 --format "value(status.url)")


# gcloud run services update $SERVICE_NAME \
#     --platform managed \
#     --region northamerica-northeast1 \
#     --set-env-vars CLOUDRUN_SERVICE_URL=$SERVICE_URL

# # sign in to /admin :get password: 
#  gcloud secrets versions access latest --secret superuser_password && echo ""

# # to run - add deploy step to yaml and 
# gcloud builds submit --config cloudbuild.yaml or add trigger
# ```
