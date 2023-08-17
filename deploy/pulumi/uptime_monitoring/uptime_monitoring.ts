import * as gcp from "@pulumi/gcp";
import { execSync } from "child_process";

const env = (env_name: string) => {
  const env_var = process.env[env_name];

  if (env_var === undefined) {
    throw new Error(
      `Expected environment variable "${env_name}" not found. Run \`source deploy/gcloud_env_var.sh\` then try again`
    );
  }

  return env_var;
};

new gcp.Provider(env("PROJECT_SERVICE_NAME"), {
  project: env("PROJECT_ID"),
  region: env("PROJECT_REGION"),
});

// asserting SKEY_SLACK_MONITOR_ALERTING_WEBHOOK exists as an env var via `env()`, but not interpolating the value in to the exec()
// command string directly. Potentially safer to let the exec child process shell handle that via the bash best-practice "${...}" pattern
env("SKEY_UPTIME_ALERT_SLACK_WEBHOOK");
const slack_alerting_webhook = execSync(
  'gcloud secrets versions access latest --secret "${SKEY_UPTIME_ALERT_SLACK_WEBHOOK}"',
  { shell: "/bin/bash", encoding: "utf8" }
);

const healthcheckRouteUptimeCheck = new gcp.monitoring.UptimeCheckConfig(
  `${env("PROJECT_SERVICE_NAME")}-https-uptime-check`,
  {
    displayName: "Uptime check over https against the app's /healthcheck route",
    monitoredResource: {
      labels: {
        host: env("DNS_DOMAIN"),
        projectId: env("PROJECT_ID"),
      },
      type: "uptime_url",
    },
    httpCheck: {
      useSsl: true,
      validateSsl: true,
      path: env("APP_HEALTHCHECK_ROUTE"),
      port: 443,
      requestMethod: "GET",
      acceptedResponseStatusCodes: [
        {
          statusClass: "STATUS_CLASS_2XX",
        },
      ],
    },
    period: "900s",
    timeout: "10s",
  }
);

const slackNotificationChannel = new gcp.monitoring.NotificationChannel(
  `${env("PROJECT_SERVICE_NAME")}-slack-webhook-alert`,
  {
    type: "webhook_tokenauth",
    displayName: `${env("PROJECT_SERVICE_NAME")} Webhook Alert Channel`,
    description: "Webhook notification channel for Cloud Run Outages",
    labels: {
      url: slack_alerting_webhook,
    },
  }
);

new gcp.monitoring.AlertPolicy(
  `${env("PROJECT_SERVICE_NAME")}-uptime-alert-policy`,
  {
    displayName: `${env("PROJECT_SERVICE_NAME")} Uptime Alerting Policy`,
    combiner: "OR",
    conditions: [
      {
        conditionThreshold: {
          aggregations: [
            {
              alignmentPeriod: "900s",
              crossSeriesReducer: "REDUCE_COUNT_FALSE",
              groupByFields: [
                "resource.label.project_id",
                "resource.label.service_name",
                "resource.label.revision_name",
                "resource.label.location",
                "resource.label.configuration_name",
              ],
              perSeriesAligner: "ALIGN_NEXT_OLDER",
            },
          ],
          comparison: "COMPARISON_GT",
          filter: `metric.labels.check_id = "${healthcheckRouteUptimeCheck.id}"`,
          thresholdValue: 0.5,
          trigger: {
            count: 1,
          },
          duration: "120s",
        },
        displayName: "Cloud Run Revision - Check passed",
      },
    ],
    notificationChannels: [slackNotificationChannel.id],
    userLabels: {
      // payload for the slack webhook, see slack's webhook documentation for format
      payload: `{"text": "Uptime check failing!"}`,
    },
  }
);
