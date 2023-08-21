import * as gcp from "@pulumi/gcp";
import * as pulumi from "@pulumi/pulumi";
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

// asserting SKEY_SLACK_MONITOR_ALERTING_WEBHOOK exists as an env var via `env()`, but not interpolating the value in to the exec()
// command string directly. Potentially safer to let the exec child process shell handle that via the bash best-practice "${...}" pattern
env("SKEY_PROD_SLACK_ALERTING_APP_TOKEN");
const slack_app_token = execSync(
  'gcloud secrets versions access latest --secret "${SKEY_PROD_SLACK_ALERTING_APP_TOKEN}"',
  { shell: "/bin/bash", encoding: "utf8" }
);

new gcp.Provider(env("PROJECT_SERVICE_NAME"), {
  project: env("PROJECT_ID"),
  region: env("PROJECT_REGION"),
});

const uptime_check_period: 60 | 300 | 600 | 900 = 60;
const healthcheckRouteUptimeCheck = new gcp.monitoring.UptimeCheckConfig(
  `${env("PROJECT_SERVICE_NAME")}-https-uptime-check`,
  {
    project: env("PROJECT_ID"),
    displayName: `Uptime check over https against the ${env(
      "PROJECT_SERVICE_NAME"
    )} app's healthcheck route`,
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
    period: pulumi.interpolate`${uptime_check_period}s`,
    timeout: "10s",
    selectedRegions: ["usa-virginia", "usa-oregon", "usa-iowa"],
  }
);

const slackNotificationChannel = new gcp.monitoring.NotificationChannel(
  `${env("PROJECT_SERVICE_NAME")}-slack-app-alert`,
  {
    project: env("PROJECT_ID"),
    type: "slack",
    displayName: `${env("PROJECT_SERVICE_NAME")} Slack Alert Channel`,
    description: "Slack notification channel for monitoring alerts",
    labels: {
      auth_token: slack_app_token,
      channel_name: env("SLACK_ALERTING_CHANNEL_NAME"),
    },
  }
);

new gcp.monitoring.AlertPolicy(
  `${env("PROJECT_SERVICE_NAME")}-uptime-alert-policy`,
  {
    project: env("PROJECT_ID"),
    displayName: `${env(
      "PROJECT_SERVICE_NAME"
    )} Healthcheck Route Uptime Alerting Policy`,
    conditions: [
      {
        displayName:
          "Alert: 50% or more of uptime check regions are unhealthy!",
        conditionThreshold: {
          filter: pulumi.interpolate`resource.type = "uptime_url" AND metric.type = "monitoring.googleapis.com/uptime_check/check_passed" AND metric.labels.check_id = "${healthcheckRouteUptimeCheck.uptimeCheckId}"`,
          // Each region in our uptime monitor produces separate metric data (as a time series). Aggregation is required before comparison
          aggregations: [
            {
              // How the time series are aligned before cross-series reduction is applied. ALIGN_NEXT_OLDER takes the nearest previous value in the series to
              // the current moment, which
              perSeriesAligner: "ALIGN_NEXT_OLDER",
              // Only aggregate as often as the uptime check may have new data
              alignmentPeriod: pulumi.interpolate`${uptime_check_period}s`,
              // Reduce to a count of check_passed === false cases in the aligned period
              crossSeriesReducer: "REDUCE_FRACTION_TRUE",
            },
          ],
          // Comperator between aggregate result and `thresholdValue`
          comparison: "COMPARISON_LT",
          // `thresholdValue` is interpreted relative to your aggregate, so here it is a percentage of healthy uptime check regions
          thresholdValue: 0.5,
          // Amount of time the trigger has to stay violated for an alert to be sent (requiring two subseqent failing uptime checks right now)
          duration: pulumi.interpolate`${uptime_check_period * 2}s`,
          // Treat missing data as a triggering event
          evaluationMissingData: "EVALUATION_MISSING_DATA_ACTIVE",
        },
      },
    ],
    combiner: "OR",
    notificationChannels: [slackNotificationChannel.id],
  }
);
