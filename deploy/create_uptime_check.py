# Be sure to auth login before running this: gcloud auth application-default login
# Also activate monitoring API & add role Monitoring Editor (roles/monitoring.editor- not needed only for console)
# roles/monitoring.uptimeCheckConfigEditor - API
# roles/monitoring.alertPolicyEditor - API
# roles/monitoring.notificationChannelEditor - API

# from google.cloud import monitoring_v3
from __future__ import print_function

import argparse
import os
import pprint

# import tabulate
from google.cloud import monitoring_v3

# from google.cloud.monitoring_v3.services.uptime_check_service import webhooks
# from google.cloud.monitoring_v3.types import uptime
# from google.protobuf import field_mask_pb2

# # from google.cloud.monitoring_v3 import MonitoredResource
# # from google.protobuf import duration_pb2

#TODO - pull these in from env_vars
PROJECT_ID="phx-01h4rr1468rj3v5k60b1vserd3"
PROJECT_SERVICE_NAME="cpho-phase2"
PROJECT_REGION="northamerica-northeast1"

display_name = "HoPiC Uptime Check test get 1"
parent = f'projects/{PROJECT_ID}'

# reference: https://cloud.google.com/monitoring/docs/samples/monitoring-uptime-check-create?hl=en#monitoring_uptime_check_create-python
# and here https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/monitoring/snippets/v3/uptime-check-client/snippets.py

# https://cloud.google.com/monitoring/api/ref_v3/rpc/google.monitoring.v3#google.monitoring.v3.UptimeCheckConfig 

# alerts https://github.com/GoogleCloudPlatform/python-docs-samples/tree/84816c5cc5b09092c2df795f367abba39c147a24/monitoring/snippets/v3/alerts-client
# https://cloud.google.com/monitoring/uptime-checks/uptime-alerting-policies?hl=en

#reference https://cloud.google.com/monitoring/api/ref_v3/rpc/google.monitoring.v3#google.monitoring.v3.UptimeCheckConfig

# https://cloud.google.com/monitoring/api/ref_v3/rpc/google.monitoring.v3#google.monitoring.v3.UptimeCheckService.CreateUptimeCheckConfig


def create_uptime_check_config_get(
    project_id: str, host_name: str = None, display_name: str = None
    ) -> uptime.UptimeCheckConfig:
    """Creates a new uptime check configuration

    Args:
        project_id: Google Cloud project id where the uptime check is created
        host_name: An example label's value for the "host" label
        display_name: A human friendly name of the configuration

    Returns:
        A structure that describes a new created uptime check
    """

    config = monitoring_v3.UptimeCheckConfig()
    config.display_name = display_name 
    config.monitored_resource = {
        "type": "cloud_run_revision",
        "labels": {
            "project_id": PROJECT_ID,
            "service_name": PROJECT_SERVICE_NAME,
            "location": PROJECT_REGION,
            # revision_name: Name of the monitored revision.
            # configuration_name: Name of the configuration which created the monitored revision.
        },

    }
    config.http_check = {
        "request_method": monitoring_v3.UptimeCheckConfig.HttpCheck.RequestMethod.GET,
        "path": "/",
    }
    config.timeout = {"seconds": 10}
    config.period = {"seconds": 900}

    client = monitoring_v3.UptimeCheckServiceClient()
    new_config = client.create_uptime_check_config(
        request={"parent": parent, "uptime_check_config": config}
    )
    pprint.pprint(new_config)
    return new_config


create_uptime_check_config_get(project_id=PROJECT_ID, display_name=display_name)
print("SUCESS YAY!!!!!!")

#NOTE: Can create in the console then get json with:
# ACCESS_TOKEN=$(gcloud auth print-access-token)
# curl -X GET "https://monitoring.googleapis.com/v3/projects/phx-01h4rr1468rj3v5k60b1vserd3/uptimeCheckConfigs" -H "Authorization: Bearer $ACCESS_TOKEN"
# This is in uptimeCheckConfig.json
#  (https://cloud.google.com/monitoring/alerts/policies-in-json?hl=en#json-uptime)

#NOTE get alert policies created in console:
$ gcloud alpha monitoring policies describe projects/phx-01h4rr1468rj3v5k60b1vserd3/alertPolicies/11166819168459470983  > test-policy.yaml
# https://cloud.google.com/sdk/gcloud/reference/alpha/monitoring/policies/list?hl=en


# Create notification channel - webhook:
# https://cloud.google.com/monitoring/alerts/using-channels-api
# Need role roles/monitoring.notificationChannelEditor

# gcloud beta monitoring channel-descriptors list --format='value(type)'
# webhook_basicauth
# webhook_tokenauth

# To set up integration with Slack via webhook, follow these instructions: https://api.slack.com/messaging/webhooks
# NOTE: With free teir for slack, the number of apps are limited. 

# Create a notification channel
# https://cloud.google.com/monitoring/alerts/using-channels-api#view-log-messages
# #Create alert 
# Name = "HoPiC Cloud Run Outage Alert"
# duration = 900s
# notification channels - google cloud console moble UserWarning

# https://cloud.google.com/monitoring/alerts/using-channels-api#monitoring_alert_delete_channel-gcloud
# gcloud beta monitoring channels create --channel-content-from-file="webhook-channel.json"
#   Or create in console (maybe prefered so no information is commited here?)


# Create alert
# (roles/monitoring.alertPolicyEditor)
# https://cloud.google.com/monitoring/alerts/policies-in-api?hl=en
# name = projects/PROJECT_ID/alertPolicies/POLICY_ID
# alerting_policy = monitoring.googleapis.com/uptime_check/check_passed
# https://monitoring.googleapis.com/v3/projects/phx-01h4rr1468rj3v5k60b1vserd3/uptimeCheckConfigs

# https://cloud.google.com/monitoring/alerts/policies-in-json?hl=en#json-uptime

