#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

# NOTE - probabaly won't work to run through without modifications - there are some manual steps. 

source $(dirname "${BASH_SOURCE[0]}")/gcloud_env_vars.sh

parent=projects/${PROJECT_ID}

# ----- MONITORING - UPTIME CHECKS ----
# NOTE: API User role need the following roles:
#   roles/monitoring.uptimeCheckConfigEditor
#   roles/monitoring.alertPolicyEditor
#   roles/monitoring.notificationChannelEditor
# (and secret accessor if storing Slack webhook url in Secret Manager)


# ----- Enable Monitoring API
gcloud services enable monitoring --project=$PROJECT_ID


# ----- Create Uptime Check (config files)
# NOTE: There can be a delay of 5 min before able to view on monitor dashbaord - https://cloud.google.com/monitoring/uptime-checks/private-checks#api:-scoping-project:~:text=delay%20of%20up%20to%205%20minutes)
# REGION_UNSPECIFIED (global)

curl -X POST "https://monitoring.googleapis.com/v3/${parent}/uptimeCheckConfigs" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @deploy/uptimeCheckConfig.json


# ----- Create a Notification Channel

# Here we're using slack (via app and webhook - https://cloud.google.com/blog/products/devops-sre/use-slack-and-webhooks-for-notifications)
# 1) Set up app and webhook (see above link).  Can test with:
#    curl -X POST -H 'Content-type: application/json' --data '{"text": "testing!"}' ${SLACK_WEBHOOK_URL}
# 2) Save slack webhook url in secret manager  - through console or:
#    Note - since won't need this secret in prod, we're setting up separately from gcloud_init_stepup.sh
# a) create temp env file
#    touch .env
# b) Add "<Your slack webhook url>" to empty .env
# c) $ gcloud secrets create slack_webhook_url --locations "${PROJECT_REGION}" --replication-policy user-managed --data-file ".env"
#    If you need to update rather than create 
#    $ gcloud secrets versions add "slack_webhook_url" --data-file ".env"
# d) Remove env file from codebase
#    $ rm -rf .env

# To access secret
gcloud secrets versions access 2 --secret="slack_webhook_url"

# Sub in slack webhook url in config (NOTE: change version (2) to correct version number)
slack_webhook_url=$(gcloud secrets versions access 2 --secret="slack_webhook_url")

config_content=$(cat deploy/webhookNotificationChannelConfig.json)
config_content_modified=$(echo "$config_content" | jq --arg url "$slack_webhook_url" '.labels.url = $url')
echo "$config_content_modified" > deploy/ackwebhookNotificationChannelConfig.json

# Create the notification channel
gcloud beta monitoring channels create --channel-content-from-file="deploy/webhookNotificationChannelConfig.json"


#----- Alert Policy
# Read back notification channel to use in alert policy: (gcloud beta monitoring channels list)
gcloud beta monitoring channels list --format json >> notification_channel_config.json
notification_channel_content=$(cat notification_channel_config.json)

# Extract the "name" field value
name=$(echo "$notification_channel_config" | jq -r '.[0].name')

# Replace notificationChannels field with name in uptimeAlertConfig
config_content=$(cat deploy/uptimeAlertConfig.json)
config_content_modified=$(echo "$config_content" | jq --arg name "$name" '.notificationChannels[0] = $name')
echo "$config_content_modified" > deploy/uptimeAlertConfig.json

# Note can also replace fields if already created --fields=[field,…]  

# Create an alert policy
# https://cloud.google.com/monitoring/alerts/types-of-conditions
gcloud alpha monitoring policies create --policy-from-file="deploy/uptimeAlertConfig.json"

gcloud alpha monitoring policies list --format json
