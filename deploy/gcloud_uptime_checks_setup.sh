# https://cloud.google.com/monitoring/uptime-checks#monitoring_uptime_check_create-api
# https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.uptimeCheckConfigs#UptimeCheckConfig
# May need to check uptime_url to also detect potential issues outside cloud run? VPC connector?

# Steps (all have configuration files in the config folder)
#   * Create uptime check
#   * 

#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

PROJECT_ID=phx-01h4rr1468rj3v5k60b1vserd3
parent=projects/${PROJECT_ID}
ACCESS_TOKEN=$(gcloud auth print-access-token)

# ----- MONITORING - UPTIME CHECKS ----
# NOTE: API User role need the following roles:
#   roles/monitoring.uptimeCheckConfigEditor
#   roles/monitoring.alertPolicyEditor
#   roles/monitoring.notificationChannelEditor
# (and secret accessor if storing Slack webhook url in Secret Manager)


# Enable Monitoring API
gcloud services enable monitoring --project=$PROJECT_ID


# Create uptime check (config files )
# NOTE: There can be a delay of 5 min before able to view on monitor dashbaord - https://cloud.google.com/monitoring/uptime-checks/private-checks#api:-scoping-project:~:text=delay%20of%20up%20to%205%20minutes)
# REGION_UNSPECIFIED (global)

curl -X POST "https://monitoring.googleapis.com/v3/${parent}/uptimeCheckConfigs" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @deploy/uptimeCheckConfig.json


# Create a notification channel (using email - via google cloud app, but idealy would have slack channel/ webhook for slack channel)
# https://cloud.google.com/blog/products/devops-sre/use-slack-and-webhooks-for-notifications
# test with curl -X POST -H 'Content-type: application/json' --data '{"text": "testing!"}' ${SLACK_WEBHOOK_URL}
# ** This is a manual step - 
#   * Save URL in secret manager

# curl -X POST "https://monitoring.googleapis.com/v3/projects/${PROJECT_ID}/notificationChannels" \
#      -H "Authorization: Bearer $ACCESS_TOKEN" \
#      -H "Content-Type: application/json" \
#      -d @deploy/webhookNotificationChannelConfig.json

gcloud beta monitoring channels create --channel-content-from-file="deploy/webhookNotificationChannelConfig.json"

# Read back notification channel to use in alert policy: (gcloud beta monitoring channels list)
gcloud beta monitoring channels list --format json >> notification_channel_config.json
notification_channel_content=$(cat notification_channel_config.json)

# Extract the "name" field
name=$(echo "$notification_channel_config" | jq -r '.[0].name')

# Replace notificationChannels field with name in uptimeAlertConfig
config_content=$(cat deploy/uptimeAlertConfig.json)
config_content_modified=$(echo "$config_content" | jq --arg name "$name" '.notificationChannels[0] = $name')
echo "$config_content_modified" > deploy/uptimeAlertConfig.json

# Note can replace fields if created --fields=[field,…]  

# Create an alert policy
# https://cloud.google.com/monitoring/alerts/types-of-conditions
gcloud alpha monitoring policies create --policy-from-file="deploy/uptimeAlertConfig.json"
