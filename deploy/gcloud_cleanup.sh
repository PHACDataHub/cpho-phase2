#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
 
# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

# WARNING: not complete, doesn't (attempt) to reset enabled APIs, revert IAM changes, or track and delete any incidental
# resources and service accounts that google creates behind the scenes. Really, this is just a quick and dirty way to
# mostly tear down a test project being used to test gcloud_init_setup.sh

allow_cleanup=false

if "${allow_cleanup}"; then
  # NOTE: using `|| :`, where : is effectively a bash no-op, to prevent errors in certain lines from exiting the script

  # ----- FRONT DOOR NETWORKING -----
  forwarding_rule_ip=$(gcloud compute addresses describe ${NETWORK_FORWARDING_IP_NAME} --format="get(address)" --global) || :
  gcloud dns record-sets transaction start --zone "${DNS_MANAGED_ZONE_NAME}" || :
  gcloud dns record-sets transaction remove "${forwarding_rule_ip}" \
   --zone "${DNS_MANAGED_ZONE_NAME}" \
   --name "${DNS_DNS_NAME}" \
   --ttl "300" \
   --type "A" || :
  gcloud dns record-sets transaction execute --zone "${DNS_MANAGED_ZONE_NAME}" || :
  gcloud compute forwarding-rules delete "${NETWORK_HTTPS_FORWARDING_RULE_NAME}" --global || :
  gcloud compute forwarding-rules delete "${NETWORK_HTTPS_FORWARDING_RULE_NAME}" --global || :
  gcloud compute target-https-proxies delete "${NETWORK_TARGET_HTTPS_PROXY_NAME}" --global || :
  gcloud compute ssl-certificates delete "${NETWORK_SSL_CERT_NAME}" --global || :
  gcloud compute url-maps delete "${NETWORK_URL_MAP_NAME}" --global || :
  gcloud compute backend-services delete "${NETWORK_BACKEND_SERVICE_NAME}" --global || :
  gcloud compute security-policies delete "${NETWORK_BASELINE_SECURITY_POLICY_NAME}" --gloabl || :
  gcloud compute network-endpoint-groups delete "${NETWORK_NEG_NAME}" --region "${PROJECT_REGION}" || :

  # ----- Cloud DNS -----
  gcloud dns managed-zones delete ${PROJECT_SERVICE_NAME} || :

  # ----- ARTIFACT REGISTRY -----
  gcloud artifacts repositories delete "${ARTIFACT_REGISTRY_REPO}" --location "${PROJECT_REGION}" || :
  
  # ----- CLOUD BUILD ----
  gcloud builds triggers delete github "${BUILD_CLOUD_BUILD_TRIGGER_NAME}" --region "${PROJECT_REGION}" || :
  
  # ----- CLOUD SQL -----
  gcloud sql instances delete "${DB_INSTANCE_NAME}" || :

  # ----- VPC NETWORK -----
  if [[ $VPC_NAME != "default" ]]; then
    gcloud compute networks delete "${VPC_NAME}" || :
  fi
  gcloud compute networks vpc-access connectors delete "${VPC_CONNECTOR_NAME}" --region "${PROJECT_REGION}" || :
  gcloud compute addresses delete "${VPC_SERVICE_CONNECTION_NAME}" || :
  
  # ----- SECRET MANAGER -----
  skey_env_var_names=$(env -0 | cut -z -f1 -d= | tr '\0' '\n' | grep "^SKEY_")
  for env_var_name in ${skey_env_var_names}; do
    delete_secret $(printenv "${env_var_name}")
  done
fi
