import os
import sys

import structlog

# See https://cloud.google.com/run/docs/tips/python#optimize_gunicorn

PORT = os.getenv("PORT", "8080")
bind = [f"0.0.0.0:{PORT}"]

# Experiment: trying k8s pods deployed with the minimal resources, and only one Django instance per container
workers = 1
threads = 1

# From the GCP docs: "timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling."
# Assume it's of simillar benefit with GKE Autopilot, TODO: determine if that's true
timeout = 0

# gunicorn's default logging configuration has a few problems:
#  1) it only adds loggers for handling gunicorn's own logs. Any other logging events, between launching the app via gunicorn
#    and the app configuring additional logging handlers, are lost.
#  2) it uses its own custom logging class with non-ideal formatting. For one thing, this leads to google cloud seeing gunicorn's
#    INFO level logs as ERROR level logs.
#
# This configuration overwrites the bad default with a sensible structlog json logging config, which will capture all logs and output
# them in a GCP logging friendly format. When the application configures its own logging later on, it will over write this config.
logconfig_dict = {
    "disable_existing_loggers": False,
    "formatters": {
        "basic_json": {
            "()": structlog.stdlib.ProcessorFormatter,
            "foreign_pre_chain": (
                structlog.contextvars.merge_contextvars,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.CallsiteParameterAdder(
                    {
                        structlog.processors.CallsiteParameter.FUNC_NAME,
                        structlog.processors.CallsiteParameter.LINENO,
                    }
                ),
                structlog.processors.UnicodeDecoder(),
            ),
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "stdout_json": {
            "level": "INFO",
            "formatter": "basic_json",
            "class": "logging.StreamHandler",
            "stream": sys.stdout,
        },
    },
    "loggers": {
        "gunicorn": {
            "propagate": True,
        },
    },
    "root": {"handlers": ["stdout_json"], "level": "INFO"},
}

wsgi_app = "server.wsgi:application"
