### Uptime Check 
Need the following roles:
* roles/monitoring.uptimeCheckConfigEditor - API
* roles/monitoring.alertPolicyEditor - API
* roles/monitoring.notificationChannelEditor - API

Uptime check - can set up in console then extract json:
https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.uptimeCheckConfigs/get?hl=en
```
ACCESS_TOKEN=$(gcloud auth print-access-token)
# curl -X GET "https://monitoring.googleapis.com/v3/projects/phx-01h4rr1468rj3v5k60b1vserd3/uptimeCheckConfigs" -H "Authorization: Bearer $ACCESS_TOKEN"
```
Then save as uptimeCheckConfig.json  

Do create uptime check with API:
```
parent=projects/phx-01h4rr1468rj3v5k60b1vserd3
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -X POST "https://monitoring.googleapis.com/v3/${parent}/uptimeCheckConfigs" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @deploy/uptimeCheckConfig.json
```
TODO Going to have to have this populated by script with variables! 

### Notification Channel 
TODO - set up GCS bucket with params or in google secret? https://cloud.google.com/blog/products/operations/write-and-deploy-cloud-monitoring-alert-notifications-to-third-party-services?_ga=2.7504250.-938591633.1690289528&_gac=1.59974239.1690811266.CjwKCAjwt52mBhB5EiwA05YKo9RJ39OgjtvUxifUtr-o_-TYSjmzz-5Lr1AsG4nRjho7by1ktNLHSxoCrXMQAvD_BwE

https://cloud.google.com/blog/products/devops-sre/use-slack-and-webhooks-for-notifications

----------------------
description: A channel that sends notifications to a webhook using token authentication.
  Token authentication includes a shared secret as a query string parameter. Token
  authentication is usually used in conjunction with SSL/TLS to reduce the risk of
  attackers snooping the token.
displayName: Webhook with Token Authentication
labels:
- description: The URL to which to publish the webhook.
  key: url
launchStage: GA
name: projects/phx-01h4rr1468rj3v5k60b1vserd3/notificationChannelDescriptors/webhook_tokenauth
type: webhook_tokenauth
-----------------

#### From slack
curl -X POST -H 'Content-type: application/json' --data '{"text": "testing!"}' "https://hooks.slack.com/services/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"

```
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -X POST "https://monitoring.googleapis.com/v3/projects/${PROJECT_ID}/notificationChannels" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @deploy/webhookNotificationChannelConfig.json
```

Use this to populate Alert policy - will need jq?

{
    "type": "webhook_tokenauth",
    "displayName": "Slack Webhook Channel",
    "description": "Webhook notification channel for Cloud Run Outages",
    "httpRequest": {
        "httpMethod": "POST",
        "url": "https://hooks.slack.com/services/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",
        "headers": {
            "Content-Type": "application/json"
        },
        "payload": "{\"text\": \"HoPiC Outage (test)!\"}"
    }
}
    "payload": "{\"text\": \"HoPiC Outage (test)!\"}"
#### Create channel (https://cloud.google.com/monitoring/alerts/using-channels-api?hl=en)
gcloud beta monitoring channels create --channel-content-from-file="deploy/webhookNotificationChannelConfig.json"

#### Read back channels 
 gcloud beta monitoring channels list

### Alert Policy 
https://cloud.google.com/monitoring/alerts/policies-in-json
gcloud alpha monitoring policies list --format=json
```
<!-- gcloud alpha monitoring policies describe projects/phx-01h4rr1468rj3v5k60b1vserd3/alertPolicies/11166819168459470983 --format="json" > deploy/alert-policy.json -->
Sub in notifications! 
gcloud alpha monitoring policies create --policy-from-file="deploy/uptimeAlertConfig.json"

POST https://monitoring.googleapis.com/v3/{name}/alertPolicies
```

# This has all the variables: https://cloud.google.com/sdk/gcloud/reference/alpha/monitoring/policies/create?hl=en
also this: https://cloud.google.com/monitoring/api/ref_v3/rest/v3/projects.alertPolicies?hl=en

gcloud alpha monitoring policies create \
    --notification-channels=[NOTIFICATION_CHANNELS,…]\
     [--aggregation=AGGREGATION --condition-display-name=CONDITION_DISPLAY_NAME --condition-filter=CONDITION_FILTER --duration=DURATION --if=IF_VALUE --trigger-count=TRIGGER_COUNT     | --trigger-percent=TRIGGER_PERCENT] [--combiner=COMBINER --display-name=DISPLAY_NAME --no-enabled --user-labels=[KEY=VALUE,…] --documentation-format=DOCUMENTATION_FORMAT; default="text/markdown" --documentation=DOCUMENTATION     | --documentation-from-file=DOCUMENTATION_FROM_FILE] [--policy=POLICY     | --policy-from-file=POLICY_FROM_FILE] [GCLOUD_WIDE_FLAG …]
```
ACCESS_TOKEN=$(gcloud auth print-access-token)
curl -X POST "https://monitoring.googleapis.com/v3/projects/${PROJECT_ID}>/alertPolicies" \
     -H "Authorization: Bearer $ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d @deploy/uptimeAlertConfig.json
     ```

https://hooks.slack.com/services/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

pass env variables: https://towardsdatascience.com/proper-ways-to-pass-environment-variables-in-json-for-curl-post-f797d2698bf3

