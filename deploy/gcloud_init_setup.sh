#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# TODO everything left here is slated to be converted to IAC/IAD

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh


# ----- Cloud DNS -----
echo ""
echo "Enable the Cloud DNS API, create a managed zone for the project, and output the project's DNS yaml"
read -n 1 -p "Type S to skip this step, anything else to continue: " dns_skip
echo ""
if [[ "${dns_skip}" != "S" ]]; then
  gcloud services enable dns.googleapis.com

  gcloud dns managed-zones create "${DNS_MANAGED_ZONE_NAME}" \
    --project "${PROJECT_ID}" \
    --description "${PROJECT_SERVICE_NAME} zone, for PHAC alpha-dns" \
    --dns-name "${DNS_DNS_NAME}" \
    --log-dns-queries \
    --visibility public

  IFS=',' read -r -a dns_name_servers <<< \
    $(gcloud dns record-sets describe "${DNS_DNS_NAME}" --zone "${DNS_MANAGED_ZONE_NAME}" --type NS --format "value[separator=\",\"](DATA)")

  dns_config_file=$(dirname "${BASH_SOURCE[0]}")/"${DNS_DOMAIN}.yaml"
  rm -rf "${dns_config_file}"

  cat <<EOT >> "${dns_config_file}"
apiVersion: dns.cnrm.cloud.google.com/v1beta1
kind: DNSRecordSet
metadata:
  name: "${DNS_NS_NAME}"
  namespace: "${DNS_PHAC_ALPHA_NS_NAME}"
spec:
  name: "${DNS_DNS_NAME}"
  type: "NS"
  ttl: 300
  managedZoneRef:
    external: "${DNS_PHAC_ALPHA_NAME}"
  rrdatas:
    - "${dns_name_servers[0]}"
    - "${dns_name_servers[1]}"
    - "${dns_name_servers[2]}"
    - "${dns_name_servers[3]}"
EOT

  echo "PHAC alpha DNS configuration output to ${dns_config_file}"
  read -n 1 -p "MANUAL STEP: open a PR adding this yaml file to the PHAC alpha DNS repo. You can do this now or later, but it needs to be merged for your new subdomain to work. Press any key to continue: " _

fi



# ----- INGRESS NETWORKING -----
# TODO Ingress networking is now a k8s concern, but it remains to look in to using Cloud Armor
# WAF rules with k8s, in which case this portion of the old script is still of value

#  # Create a Cloud Armor security policy bucket, to be populated with a bunch of sensible defaults for a web app ingress load balancer
#  # TODO do our GCP org level policies already apply anything to our load balancers?
#  # TODO do we subscribe to "Google Cloud Armor Managed Protection Plus"? If so, additional features/managed security policies we can enable
#  # TODO additional custom policies we could set up?
#  gcloud compute security-policies create "${INGRESS_BASELINE_SECURITY_POLICY_NAME}" \
#    --description "Secuirty policy with sensible baseline configuration for an external load balancer" \
#    --global
#  preconfigured_waf_rules=(
#    # opt out of rules for special character limits in cookies (942420, 942421, 942432); lots of false positives from these
#    # opt out of rules for SQL injection probing (942330, 942370, 942490); lots of false positives from these
#    "'sqli-v33-stable', {'opt_out_rule_ids': ['owasp-crs-v030301-id942420-sqli', 'owasp-crs-v030301-id942421-sqli', 'owasp-crs-v030301-id942432-sqli' 'owasp-crs-v030301-id942330-sqli', 'owasp-crs-v030301-id942370-sqli', 'owasp-crs-v030301-id942490-sqli']}"
#    "'xss-v33-stable'"
#    "'lfi-v33-stable'"
#    "'rfi-v33-stable'"
#    "'rce-v33-stable'"
#    "'methodenforcement-v33-stable'"
#    "'scannerdetection-v33-stable'"
#    "'protocolattack-v33-stable'"
#    "'sessionfixation-v33-stable'"
#    # TODO these do not apply, but is there any latency cost to still scanning for them? Maybe enable them anyway
#    #"'php-v33-stable'" 
#    #"'java-v33-stable'" 
#    #"'nodejs-v33-stable'" 
#  )
#  declare -i level_incrementor=9000
#  for rule in "${preconfigured_waf_rules[@]}"; do
#    gcloud compute security-policies rules create "${level_incrementor}" \
#      --security-policy "${INGRESS_BASELINE_SECURITY_POLICY_NAME}" \
#      --expression "evaluatePreconfiguredWaf(${rule})" \
#      --action deny-403
#    
#    level_incrementor+=1
#  done
#  gcloud compute backend-services update "${INGRESS_BACKEND_SERVICE_NAME}"\
#    --security-policy "${INGRESS_BASELINE_SECURITY_POLICY_NAME}" \
#    --global



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

  # Enable Artifact Registry vulnerability scanning 
  gcloud services enable containerscanning.googleapis.com
fi



# ----- CLOUD STORAGE -----
echo ""
echo "Create a Google Cloud Storage bucket for test coverage reports"
read -n 1 -p "Type S to skip this step, anything else to continue: " coverage_bucket_skip
echo ""
if [[ "${coverage_bucket_skip}" != "S" ]]; then
  gcloud services enable storage.googleapis.com

  gcloud storage buckets create "gs://${TEST_COVERAGE_BUCKET_NAME}" --location "${PROJECT_REGION}"
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
    sqladmin.googleapis.com \
    cloudresourcemanager.googleapis.com 
   
   # Set necessary roles for Cloud Build service account, including custom 
   #TODO - modify permissions & roles (i.e roles/run) to be "least-privileged"
  cloud_build_project_roles=("roles/cloudbuild.serviceAgent" "roles/artifactregistry.writer" "roles/run.admin")
  for role in "${cloud_build_project_roles[@]}"; do
     cloud projects add-iam-policy-binding "${PROJECT_ID}" \
      --member "serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
      --role "${role}"
  done

  # Give Cloud Build read-write to the test coverage bucket
  cloud_build_coverage_bucket_roles=("roles/storage.objectCreator" "roles/storage.legacyBucketReader")
  for role in "${cloud_build_coverage_bucket_roles[@]}"; do
    gcloud storage buckets add-iam-policy-binding "gs://${TEST_COVERAGE_BUCKET_NAME}" \
     --member "serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
     --role "${role}"
  done

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
fi



# ----- CLOUD TRACE -----
echo ""
echo "Enable the Cloud Trace API"
read -n 1 -p "Type S to skip this step, anything else to continue: " trace_skip
echo ""
if [[ "${trace_skip}" != "S" ]]; then
  gcloud services enable cloudtrace.googleapis.com
fi



# ----- UPTIME MONITORING -----
echo ""
echo "Create uptime monitoring and outage alerting"
read -n 1 -p "Type S to skip this step, anything else to continue: " uptime_skip
echo ""
if [[ "${uptime_skip}" != "S" ]]; then
  read -n 1 -p "MANUAL STEP: requires a slack app with the chat:write scope for alerting. MANUALLY store the slack app bot user's oauth token in the project Secret Manager with the key \"${SKEY_PROD_SLACK_ALERTING_APP_TOKEN}\". Press any key to continue: " _
  echo ""

  (cd pulumi && npm run create-uptime-monitoring)
fi
