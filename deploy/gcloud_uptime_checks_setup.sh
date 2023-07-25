# https://cloud.google.com/monitoring/uptime-checks#monitoring_uptime_check_create-api
# https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.uptimeCheckConfigs#UptimeCheckConfig
# May need to check uptime_url to also detect potential issues outside cloud run? VPC connector?

#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

PROJECT_ID = phx-01h4rr1468rj3v5k60b1vserd3

# Create config file https://levelup.gitconnected.com/injecting-environment-variables-into-static-files-ea21c2d4bdbd#:~:text=The%20goal%20is%20to%20easily,the%20variables%20during%20build%20time.
# ----- MONITORING - UPTIME CHECKS ----
echo ""
echo "Enable Monitoring, Cloud Run Uptime Checks"
read -n 1 -p "Type S to skip this step, anything else to continue: " uptime_checks_skip
echo ""
if [[ "${uptime_checks_skip}" != "S" ]]; then

# API User role need the following roles:
# roles/monitoring.uptimeCheckConfigEditor
# roles/monitoring.alertPolicyEditor
# roles/monitoring.notificationChannelEditor

# REGION_UNSPECIFIED (global)

# Enable monitoring API
gcloud services enable monitoring --project=$PROJECT_ID
  
# Create uptime check (curl config) (NOTE: Can be a delay of 5 min before able to view on monitor dashbaord - https://cloud.google.com/monitoring/uptime-checks/private-checks#api:-scoping-project:~:text=delay%20of%20up%20to%205%20minutes)
curl https://monitoring.googleapis.com/v3/projects/${PROJECT_ID}/uptimeCheckConfigs \
-H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
--request POST --data '{
"displayName": "private-check-demo",
"monitoredResource": {
  "type": "servicedirectory_service",
  "labels": {
    "project_id": "'"$PROJECT_ID"'",
    "service_name": "PRIVATE_SERVICE",
    "namespace_name": "PRIVATE_NAMESPACE",
    "location": "REGION"
  }
},
"httpCheck": {
  "requestMethod": "GET"
},
"period": "60s",
"timeout": "10s",
"checker_type": "VPC_CHECKERS"
}'

# Create alert for uptime check
