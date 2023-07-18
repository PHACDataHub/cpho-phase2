#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh



# TODO replace with Infrastructure as Code/Data, after the options are discussed and we agree on one (with app devs included in discussion)



# ----- ARTIFACT REGISTRY -----
echo ""
echo "Enable Artifact Registry to store container images for Cloud Run to use"
read -n 1 -p "Type S to skip this step, anything else to continue: " artifact_skip
echo ""
if [[ "${artifact_skip}" != "S" ]]; then
  gcloud services enable artifactregistry.googleapis.com
  
  # Create Artifact Repo within the Artifact Registry
  gcloud artifacts repositories create $ARTIFACT_REGISTRY_REPO \
     --location "${PROJECT_REGION}" \
     --description "${ARTIFACT_REGISTRY_REPO}" \
     --repository-format docker 
  
  # Authorize local docker client to push/pull images to artifact registry
  gcloud auth configure-docker "${PROJECT_REGION}-docker.pkg.dev"
fi



# ----- CLOUD BUILD ----
echo ""
echo "Enable Cloud Build, triggered by GitHub pushes"
read -n 1 -p "Type S to skip this step, anything else to continue: " build_skip
echo ""
if [[ "${build_skip}" != "S" ]]; then
  gcloud services enable \
    cloudbuild.googleapis.com \
    sourcerepo.googleapis.com \
    cloudresourcemanager.googleapis.com

  # Custom role allowing use of `gcloud sql instances list`, necessary for the build workflow to use ./make_prod_env_file.sh
  # Note: relevant APIs must be enabled before a corresponding IAM role can be created, it seems
  gcloud services enable \
    sql-component.googleapis.com \
    sqladmin.googleapis.com 
   
   # Set necessary roles for Cloud Build service account, including custom 
  cloud_build_roles=("roles/cloudbuild.serviceAgent" "roles/artifactregistry.writer" "roles/run.admin")
  for role in "${cloud_build_roles[@]}"; do
     gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
       --member "serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
       --role "${role}"
  done

  # Give Cloud Build access to the Cloud Run service account
  gcloud iam service-accounts add-iam-policy-binding "${PROJECT_NUMBER}"-compute@developer.gserviceaccount.com \
    --member "serviceAccount:"${PROJECT_NUMBER}"@cloudbuild.gserviceaccount.com" \
    --role "roles/iam.serviceAccountUser"

  echo ""
  read -n 1 -p "MANUAL STEP: you will need to manually add the appropriate GitHub connection via the GCP dashboard, under \"Cloud Build > Repositories\". Press any key to continue: " _

  # Connect to the repository can possibly be done more programatically, but it's messy and might need bot GitHub accounts we don't have
  # Just make the connection manually for now
  echo ""
  read -n 1 -p "If the GitHub connection has been manually created, we can configure the on-push build trigger. If the connection hasn't been made, skip this. Type S to skip, or any other key to continue: " trigger_skip
  echo ""

  if [[ "${trigger_skip}" != "S" ]]; then
    # Add cloud build trigger (this is set to be triggered on push to main branch)
    gcloud builds triggers create github \
      --name "${BUILD_CLOUD_BUILD_TRIGGER_NAME}" \
      --region "${PROJECT_REGION}" \
      --repo-name "${BUILD_GITHUB_REPO_NAME}" \
      --repo-owner "${BUILD_GITHUB_REPO_OWNER}" \
      --build-config "${BUILD_CLOUD_BUILD_CONFIG_PATH}" \
      --branch-pattern ".*" \
      --include-logs-with-status \
      --no-require-approval
  fi

  # Code coverage reporting with Codecov in with Cloud Build
  echo ""
  echo "Enable Test Coverage Reporting to be captured by Cloud Build with Codecov."
  read -n 1 -p "Type S to skip this step, anything else to continue: " build_codecov
  echo ""
  
  if [[ "${build_codecov}" != "S" ]]; then
    echo ""
    read -n 1 -p "OPTIONAL & MANUAL STEP: you will need to manually generate a codecov token if one hasn't already been set up for the project. To do this, go to https://about.codecov.io/sign-up/ to link GitHub, and then generate token for uploading the test coverage report. Be sure to set CODECOV_TOKEN in the GCP Secret Manager. Press any key to continue: " _
    # Enable secret manager first
    # Create GCP secret: gcloud secrets create "SKEY_CODECOV_TOKEN" --replication-policy="user-managed" --locations="${PROJECT_REGION}"
    # add version: echo -n "<put code here>" | gcloud secrets versions add SKEY_CODECOV_TOKEN --data-file=-   (https://cloud.google.com/secret-manager/docs/add-secret-version)
    # to read back (need secret accessor role): gcloud secrets versions access latest --secret "${key}"
    echo ""
    ##TODO - add step to add secret now to GCP
  fi

  # Allow Cloud Build access to secret
  gcloud secrets add-iam-policy-binding "CODECOV_TOKEN" \
  --member "serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role roles/secretmanager.secretAccessor
fi



# ----- CLOUD STORAGE (optional) -----
if [ ! $PROJECT_IS_USING_WHITENOISE ]; then
  echo ""
  echo "Create a media bucket"
  read -n 1 -p "Type S to skip this step, anything else to continue: " bucket_skip
  echo ""
  if [[ "${bucket_skip}" != "S" ]]; then
    gsutil mb -l "${PROJECT_REGION}" "gs://${MEDIA_BUCKET_NAME}"
  fi
fi



# ----- VPC NETWORK -----
echo ""
echo "Create and configure the project's VPC Network"
read -n 1 -p "Type S to skip this step, anything else to continue: " vpc_skip
echo ""
if [[ "${vpc_skip}" != "S" ]]; then
  gcloud services enable \
    servicenetworking.googleapis.com \
    vpcaccess.googleapis.com

  if [[ "${VPC_NAME}" != "default" ]]; then
    echo "Unless a reason _not_ to use the project's default network is identified, stick to using it. Creating a new VPC, and getting it right, will be tricky"
    exit 1
  fi

  # Create an IP range within the VPC network, from which the SQL instance's internal IP will be assigned and
  # to which a serverless VPC access connector will be attached, for the Cloud Run services to connect through
  gcloud compute addresses create "${VPC_SERVICE_CONNECTION_NAME}" \
    --project "${PROJECT_ID}" \
    --global \
    --network "${VPC_NAME}" \
    --purpose VPC_PEERING \
    --prefix-length 24

  # Peer the new VPC network private address range to google's Service Networking service. The Service Networking service
  # own and manages the VPC networks created for managed/serverless assets such as Cloud Run. Without this peering,
  # VPC access connectors between the two will not be usable
  gcloud services vpc-peerings connect \
    --project "${PROJECT_ID}" \
    --network "${VPC_NAME}" \
    --ranges "${VPC_SERVICE_CONNECTION_NAME}" \
    --service servicenetworking.googleapis.com

  # Create a VPC access connector so that the Cloud Run instances can connect through to addresses inside the project VPC
  gcloud compute networks vpc-access connectors create "${VPC_CONNECTOR_NAME}" \
    --project "${PROJECT_ID}" \
    --region "${PROJECT_REGION}" \
    --network "${VPC_NAME}" \
    --range "${VPC_CONNECTOR_RANGE}"
fi



# ----- CLOUD SQL -----
echo ""
echo "Enable the Cloud SQL API, create a database and user"
read -n 1 -p "Type S to skip this step, anything else to continue: " sql_skip
echo ""
if [[ "${sql_skip}" != "S" ]]; then
  # Enable APIs
  gcloud services enable \
    sql-component.googleapis.com \
    sqladmin.googleapis.com \
    secretmanager.googleapis.com
  
  set_secret "${SKEY_DB_ROOT_PASSWORD}" $(openssl rand -base64 80)

  # Create Postgres instance (beta track necesary to use --allocated-ip-range-name currently)
  gcloud beta sql instances create "${DB_INSTANCE_NAME}" \
    --project "${PROJECT_ID}" \
    --region "${PROJECT_REGION}" \
    --database-version "${DB_VERSION}" \
    --tier "${DB_TIER}" \
    --root-password $(get_secret "${SKEY_DB_ROOT_PASSWORD}") \
    --network "${VPC_NAME}" \
    --no-assign-ip \
    --allocated-ip-range-name "${VPC_SERVICE_CONNECTION_NAME}" \
    --enable-google-private-path
  
  # Create Database
  gcloud sql databases create "${DB_NAME}" \
    --instance "${DB_INSTANCE_NAME}"
  
  # This secret is short lived, to be deleted once the value has been saved in the .env.prod secret
  # Storing it as a secret here is just in case this script exits before the whole .env.prod is written
  set_secret "${SKEY_DB_USER_PASSWORD}" $(openssl rand -base64 80)

  # Create User
  gcloud sql users create "${DB_USER}" \
    --instance "${DB_INSTANCE_NAME}" \
    --password $(get_secret "${SKEY_DB_USER_PASSWORD}")
fi



# ----- DNS -----
# TODO


# ----- SECRET MANAGER -----
echo ""
echo "Create and save .env.prod in Secret Manager"
read -n 1 -p "Type S to skip this step, anything else to continue: " secrets_skip
echo ""
if [[ "${secrets_skip}" != "S" ]]; then
  gcloud services enable secretmanager.googleapis.com
  
  # Construct the .env.prod file to store in Secret Manager, using a temp file with a cleanup exit trap to make sure it doesn't stay on-disk
  tmp_prod_env=$(mktemp -t .env.prod.XXXX)
  function cleanup {
    rm -rf "${tmp_prod_env}"
  }
  trap cleanup EXIT

  bash_escape "DB_NAME=${DB_NAME}" >> "${tmp_prod_env}"
  bash_escape "DB_USER=${DB_USER}" >> "${tmp_prod_env}"
  bash_escape "DB_PASSWORD=$(get_secret "${SKEY_DB_USER_PASSWORD}")" >> "${tmp_prod_env}"
  bash_escape "DB_HOST=$(gcloud sql instances list --filter name:"${DB_INSTANCE_NAME}" --format "value(PRIVATE_ADDRESS)")" >> "${tmp_prod_env}"
  bash_escape "DB_PORT=5432" >> "${tmp_prod_env}"
  
  bash_escape "SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')" >> "${tmp_prod_env}"
  
  # TODO: the ALLOWED_HOSTS configuration will be simpler once the DNS step is in place
  service_url=$(gcloud run services describe "${PROJECT_SERVICE_NAME}" --platform managed --region "${PROJECT_REGION}" --format "value(status.url)" || echo "")
  if [[ ! -z $service_url ]]; then
    # Need to strip the https:// from the URL, just want the host portion
    ALLOWED_HOSTS=$(echo "${service_url}" | sed 's/^https:\/\///')
  else
    echo "Prior to the first cloud run deploy, the service doesn't exist yet and it's URL is unknown, but a valid config is needed to get the service deployed that first time. A placeholder is used in the initial .env.prod secret, so you'll have to update the Secret Manager value once you know the actual URL."
    ALLOWED_HOSTS="placeholder.not-a-tld"
  fi
  bash_escape "ALLOWED_HOSTS=${ALLOWED_HOSTS}" >> "${tmp_prod_env}"
  
  if [[ ! $PROJECT_IS_USING_WHITENOISE ]]; then
    bash_escape "MEDIA_BUCKET_NAME=${MEDIA_BUCKET_NAME}" >> "${tmp_prod_env}"
  fi

  if [[ -n $(gcloud secrets describe --verbosity none "${SKEY_PROD_ENV_FILE}")  ]]; then
    gcloud secrets versions add "${SKEY_PROD_ENV_FILE}" --data-file "${tmp_prod_env}"
  else
    gcloud secrets create --locations "${PROJECT_REGION}" --replication-policy user-managed "${SKEY_PROD_ENV_FILE}" --data-file "${tmp_prod_env}"
  fi

  # Not strictly necessary with the exit trap, but may as well delete this quickly once it's served it's purpose
  rm -rf "${tmp_prod_env}"

  # Only want one source of truth for this, can be deleted now that it is also in the .env.prod secret
  delete_secret "${SKEY_DB_USER_PASSWORD}"
fi



# ----- CLOUD RUN -----
echo ""
echo "Enable the Cloud Run API"
read -n 1 -p "Type S to skip this step, anything else to continue: " run_skip
echo ""
if [[ "${run_skip}" != "S" ]]; then
  gcloud services enable \
    run.googleapis.com \
    compute.googleapis.com

  # Give the Cloud Run service account access to the necessary prod env secrets
  gcloud secrets add-iam-policy-binding "${SKEY_PROD_ENV_FILE}" \
    --member "serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role roles/secretmanager.secretAccessor
fi
