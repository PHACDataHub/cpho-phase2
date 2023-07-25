# https://cloud.google.com/monitoring/uptime-checks#monitoring_uptime_check_create-api
# https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.uptimeCheckConfigs#UptimeCheckConfig

#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# Create config file https://levelup.gitconnected.com/injecting-environment-variables-into-static-files-ea21c2d4bdbd#:~:text=The%20goal%20is%20to%20easily,the%20variables%20during%20build%20time.
# ----- MONITORING - UPTIME CHECKS ----
echo ""
echo "Enable Monitoring, Cloud Run Uptime Checks"
read -n 1 -p "Type S to skip this step, anything else to continue: " uptime_checks_skip
echo ""
if [[ "${uptime_checks_skip}" != "S" ]]; then

API User role 
roles/monitoring.uptimeCheckConfigEditor
roles/monitoring.alertPolicyEditor
roles/monitoring.notificationChannelEditor

REGION_UNSPECIFIED (global)
#   gcloud services enable \
#     cloudbuild.googleapis.com \
#     sourcerepo.googleapis.com \
#     cloudresourcemanager.googleapis.com

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
