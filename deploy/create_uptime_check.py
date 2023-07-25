# reference: https://cloud.google.com/monitoring/docs/samples/monitoring-uptime-check-create?hl=en#monitoring_uptime_check_create-python
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
    project_id = "phx-01h4rr1468rj3v5k60b1vserd3"
    display_name = "HoPiC Uptime Check"
    host_name = " "

    config = monitoring_v3.UptimeCheckConfig()
    config.display_name = display_name or "New GET uptime check"
    config.monitored_resource = {
        # "type": "uptime_url",
        # "labels": {"host": host_name or "example.com"},
        "type": "Cloud Run Service"

    }
    config.http_check = {
        "request_method": monitoring_v3.UptimeCheckConfig.HttpCheck.RequestMethod.GET,
        "path": "/",
    }
    config.timeout = {"seconds": 10}
    config.period = {"seconds": 300}

    client = monitoring_v3.UptimeCheckServiceClient()
    new_config = client.create_uptime_check_config(
        request={"parent": project_id, "uptime_check_config": config}
    )
    pprint.pprint(new_config)
    return new_config


def create_uptime_check_config_post(
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
    config.display_name = display_name or "New POST uptime check"
    config.monitored_resource = {
        "type": "uptime_url",
        "labels": {"host": host_name or "example.com"},
    }
    config.http_check = {
        "request_method": monitoring_v3.UptimeCheckConfig.HttpCheck.RequestMethod.POST,
        "content_type": monitoring_v3.UptimeCheckConfig.HttpCheck.ContentType.URL_ENCODED,
        # "body": "foo=bar".encode("utf-8"),
        "path": "/",
        # "port": 80,
    }
    config.timeout = {"seconds": 10}
    config.period = {"seconds": 300}

    #want log check failures 
    log_check_failures = True
    response_timeout = 10s

    client = monitoring_v3.UptimeCheckServiceClient()
    new_config = client.create_uptime_check_config(
        request={"parent": project_id, "uptime_check_config": config}
    )
    pprint.pprint(new_config)
    return new_config

#Create alert 
Name = "HoPiC Uptime Alert uptime failure"
duration = 60s
notification channels - google cloud console moble UserWarning

Target
Response
Alert 

