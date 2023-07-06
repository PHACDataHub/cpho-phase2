#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset
 
# ----- Get configuration variables + secrets helpers -----
source ./deploy/gcloud_env_vars.sh

# NOTE: using `|| :`, where : is effectively a bash no-op, to prevent errors in certain lines from exiting the script

# ----- ARTIFACT REGISTRY -----
# TODO back up first (move X latest images to cold storage?), set some TTL on that?
# TODO revert permissions to default, disable API?
gcloud artifacts repositories delete ${ARTIFACT_REGISTRY_REPO} --location ${PROJECT_REGION} || :

# ----- CLOUD BUILD ----
# TODO maybe also find and delete the project's repository connection object?
# TODO revert permissions to default, disable API?
gcloud builds triggers delete github ${BUILD_CLOUD_BUILD_TRIGGER_NAME} || :

# ----- CLOUD RUN -----
# TODO revert permissions to default, disable API?

# ----- CLOUD STORAGE -----
# TODO might not be worth deleting, at least not immediately. Won't be costing much
# Set some reasonable TTL so it takes care of itself?

# ----- CLOUD SQL -----
# TODO back up first?
# TODO revert permissions to default, disable API?
gcloud sql instances delete ${DB_INSTANCE_NAME} || :

# ----- VPC NETWORK -----
if [[ $VPC_NAME != "default" ]]; then
  gcloud compute networks delete ${VPC_NAME} || :
fi
gcloud compute networks vpc-access connectors delete ${VPC_CONNECTOR_NAME} --region ${PROJECT_REGION} || :

# ----- SECRET MANAGER -----
SKEY_ENV_VAR_NAMES=$(env -0 | cut -z -f1 -d= | tr '\0' '\n' | grep "^SKEY_")
for ENV_VAR_NAME in ${SKEY_ENV_VAR_NAMES}; do
  delete_secret $(printenv ${ENV_VAR_NAME})
done
