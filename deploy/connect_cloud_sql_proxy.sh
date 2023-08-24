#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

# ----- Get configuration variables + secrets helpers -----
source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

echo ""
echo "Checking path for cloud-sql-proxy dependency"
if ! which cloud-sql-proxy; then
  echo "Path does not contain cloud-sql-proxy! Follow these docs to install it: https://cloud.google.com/sql/docs/mysql/sql-proxy#linux-64-bit"
  exit 1
fi

local_access_env_path=$(dirname "${BASH_SOURCE[0]}")/../server/.env.prod

function cleanup {
  echo ""
  echo "Deleting temporary app env file"
  rm -f "${local_access_env_path}"

  echo ""
  echo "Revoking temporary credentials used for cloud-sql-proxy"
  gcloud auth application-default revoke --quiet
  
  echo ""
  echo "Clearing authorized public IPs and disabling the DB's public IP"
  gcloud sql instances patch "${DB_INSTANCE_NAME}" --clear-authorized-networks --no-assign-ip --quiet
}
trap cleanup EXIT

echo ""
echo "Starting DB backup. Note: manual backups are not deleted automatically, may require periodic cleanup"
gcloud sql backups create --instance "${DB_INSTANCE_NAME}" --description "Triggered by connect_cloud_sql_proxy.sh"

echo ""
echo "Enabling public IP for database instance, configured to only accept traffic from your current external IP"
# Your system doesn't usually know it's own external ip, need to send a packet out of your network, and then
# ask whoever received it what they see it as (on the far side of your router, ISP, any other intermediate networks, etc)
# ... so we're trusting that ipinfo.io doesn't lie to us. If we keep this approach long term, maybe we host our own IP reflector? 
your_external_ip=$(curl https://ipinfo.io/ip)
gcloud sql instances patch "${DB_INSTANCE_NAME}" --assign-ip --authorized-networks "${your_external_ip}"  --quiet

echo ""
echo "Getting a temporary env file that configures the local dev app for prod DB access, written to ${local_access_env_path}"
gcloud secrets versions access latest --secret "${SKEY_LOCAL_ACCESS_PROD_ENV_FILE}" --out-file "${local_access_env_path}"

echo ""
echo "Getting temporary credentials for cloud-sql-proxy (oauth step)"
gcloud auth application-default login

echo ""
echo "Connecting via cloud-sql-proxy. The database will be available via localhost at port ${LOCAL_ACCESS_DB_PORT}"
cloud_sql_connection_name=$(gcloud sql instances describe "${DB_INSTANCE_NAME}" --format 'value(connectionName)')
cloud-sql-proxy "${cloud_sql_connection_name}" --address 127.0.0.1 --port "${LOCAL_ACCESS_DB_PORT}"
