#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# TODO everything left here is slated to be converted to IAC/IAD

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh


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
